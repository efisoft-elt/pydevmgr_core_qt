from dataclasses import dataclass
from enum import Enum
import sys
from typing import List, Optional, Tuple, Union
from PyQt5.QtWidgets import QApplication, QComboBox, QFrame, QLabel, QVBoxLayout, QWidget
from PyQt5 import QtCore, uic
from pydantic.main import BaseModel
from pydevmgr_core.base.base import BaseObject, find_factories
from pydevmgr_core import create_data_model, nodes, set_data_model, storedproperty
from pydevmgr_core.base.datamodel import DataLink
from pydevmgr_core.base.device import BaseDevice
from pydevmgr_core.base.download import Downloader
from pydevmgr_core.base.node import BaseNode
from pydevmgr_core.base.object_path import ObjPath
from pydevmgr_elt.base.eltdevice import open_elt_device
from pydevmgr_tools.action import Action, ActionMap, ActionEnum
from systemy.system import BaseFactory
from pydevmgr_core_qt import elements
from pydevmgr_core_qt.appenders import ToLayout
from pydevmgr_core_qt.connectors import QtButtonConnector
from pydevmgr_core_qt.feedbacks import QtTextFeedback
from pydevmgr_core_qt.qt_objects.action import QtLinkedAction
from pydevmgr_core_qt.qt_objects.base import QtBase, get_connection_pairs
from pydevmgr_core_qt.qt_objects.connection import  Connector 

from pydevmgr_core_qt.qt_objects.device import QtDevice
from pydevmgr_core_qt.qt_objects.device_factory import QtDeviceFactory, register_qtdevice
from pydevmgr_core_qt.qt_objects.engine import WidgetMaker
from pydevmgr_core_qt.qt_objects.interface import QtInterface
from pydevmgr_core_qt.qt_objects.node import QtNode
from pydevmgr_core_qt.qt_objects.node_factory import QtNodeFactory 


from pydevmgr_elt.base.eltstat import StateInfo
from pydevmgr_core_qt.style import Style, get_style


from pydevmgr_tools.getter import BaseGetter, register_getter 
from pydevmgr_tools.setter import BaseSetter, register_setter 

from pydevmgr_elt import Motor 
from pydevmgr_elt.base.config import GROUP 

@register_setter(QLabel, StateInfo)
@dataclass
class StateInfoSetter(BaseSetter):
  def set(self, widget: QWidget, ctg: StateInfo ):
        code, text, group = ctg 
        widget.setText( f"{code}: {text}" )
        widget.setStyleSheet(get_style(group))   


class MOVE_MODE(int, Enum):
    ABSOLUTE = 0
    RELATIVE = 1
    VELOCITY = 2


class COMMAND(int, Enum):
    _ = -1
    INIT = 0 
    ENABLE = 1 
    DISABLE = 2
    RESET = 3
    
 


class QtMotorWidget(QFrame):
    def __init__(self,*args, **kwargs):
        QFrame.__init__(self, *args, **kwargs)
        uic.loadUi('/Users/guieus/dev/pydevmgr/pydevmgr_elt_qt/pydevmgr_elt_qt/uis/motor_ctrl_frame.ui', self) 


class Move(QtLinkedAction):
    def link(self, motor: Motor)->None:
        parent = self.get_parent()

        def move(mode, pos, vel):
            if mode ==  MOVE_MODE.ABSOLUTE:
                motor.move_abs(pos, vel)
            elif mode == MOVE_MODE.RELATIVE:
                motor.move_rel(pos, vel)
            elif mode == MOVE_MODE.VELOCITY:
                motor.move_vel(vel)
            parent.refresh()
        
        feedback = parent.feedback  
        parent.ctrl.position.set(0.0) 
        parent.ctrl.velocity.set(1.0)
        self.set_action( Action( move, [parent.ctrl.move_mode, parent.ctrl.position, parent.ctrl.velocity], feedback=feedback ) )
          
class Stop(QtLinkedAction):
    def link(self, motor:Motor)->None:
        feedback = self.get_parent().feedback 
        self.set_action( Action( motor.stop, feedback=feedback) )


class ChangeState(QtLinkedAction):
    def link(self, device: BaseDevice):
        parent = self.get_parent()
        def reset_menu():
            parent.ctrl.command.widget.setCurrentIndex(0)
        
        feedback = parent.feedback

        state_action = ActionEnum( after=reset_menu)
        state_action.add_action( COMMAND.INIT, Action(device.init, feedback=feedback))
        state_action.add_action( COMMAND.ENABLE, Action(device.enable, feedback=feedback))
        state_action.add_action( COMMAND.DISABLE, Action(device.disable, feedback=feedback))
        state_action.add_action( COMMAND.RESET, Action(device.reset, feedback=feedback))
        self.set_action( state_action) 


class MoveByName(QtLinkedAction):
    def link(self, motor:Motor):
        parent = self.get_parent()
        feedback = parent.feedback
        
        self.widget.addItems( [""]+list(motor.posnames) )
        posname_action = ActionMap( after= lambda :self.widget.setCurrentIndex(0) )
        for posname in motor.posnames:
            posname_action.add_action( posname, Action( motor.move_name, [posname, parent.ctrl.velocity], feedback=feedback ))
        self.set_action( posname_action )      

class TogleIgnore(QtLinkedAction):
     def link(self, device:BaseDevice):
        parent = self.get_parent()
        action  = Action( device.is_ignored.set , [parent.is_ignored] )
        self.set_action(action) 

v = nodes.Value(value=9)

@register_qtdevice( Motor, "ctrl")
@set_data_model(name="DataIn",  exclude={"ctrl"})
@set_data_model(name="DataOut", include={})
class QtMotor(QtDevice):
    @classmethod
    def get_widget_class(cls):
        return QtMotorWidget

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.feedback = QtTextFeedback( self.ctrl.feedback )
        # make sure to touch all QtNodes so they are build 
        list(self.find( QtNode, -1))
            
    @storedproperty
    def feedback(self):
        return QtTextFeedback( self.ctrl.feedback )
    
            

    @set_data_model
    class Stat(QtInterface):
        pos_actual = QtNodeFactory(vtype=float, origin="pos_actual", widget="pos_actual", format="%.3f")
        pos_target = QtNodeFactory(vtype=float, origin="pos_target", widget="pos_target", format="%.3f")
        pos_error  = QtNodeFactory(vtype=float, widget="pos_error",  format="%.3f")
        vel_actual = QtNodeFactory(vtype=float, widget="vel_actual",  format="%.3f")
        pos_name   = QtNodeFactory(vtype=str, widget="posname")
       
        state_info = QtNodeFactory(vtype=StateInfo, widget="state", mode="s" )
        substate_info = QtNodeFactory(vtype=StateInfo, widget="substate", mode="s" )
        error_info = QtNodeFactory(vtype=StateInfo, widget="error_txt", mode="s" )
        
    @set_data_model
    class Ctrl(QtInterface):
        position  =  QtNodeFactory(vtype=float, widget="input_pos_target", format="%.3f")
        velocity =  QtNodeFactory(vtype=float, widget="input_velocity",  format="%.3f")

        move_mode = QtNodeFactory( vtype=(MOVE_MODE, MOVE_MODE.ABSOLUTE), widget="move_mode") 
        
        feedback = QtNodeFactory(vtype=str, widget="rpc_feedback")
        command = QtNodeFactory(vtype=(COMMAND, COMMAND._ ), widget="state_action", clear=True)
        posname = QtNodeFactory(vtype=str, widget="move_by_posname", clear=True)
        
        toto = QtNodeFactory(vtype=float, origin=v, widget=WidgetMaker(QLabel), appender=ToLayout("verticalLayout"))
        backlash = QtNodeFactory(vtype=float, origin="backlash", widget=elements.QValueLabel,
                appender=ToLayout("verticalLayout"),
                label="backlash", unit="mm"
                )

    
    is_ignored = QtNodeFactory( vtype=bool, origin="is_ignored", widget="check", reverse=True)
    
    name = QtNodeFactory( vtype=str, widget="name")
    move = Move.Config( widget="move")
    stop = Stop.Config( widget="stop")
    change_state = ChangeState.Config( widget="state_action") 
    move_by_name = MoveByName.Config( widget="move_by_posname")
    togle_ignore = TogleIgnore.Config( widget="check")   
 
    stat= Stat.Config(origin="stat",implicit="origin")
    ctrl = Ctrl.Config(origin="cfg")
    
    def refresh(self):
        enable_pos = self.ctrl.move_mode.get()!=MOVE_MODE.VELOCITY
        self.ctrl.position.widget.setEnabled(enable_pos)
        # if device:
        #     if device.is_ignored.get() != self.ctrl.is_ignored.get():
        #         self.ctrl.is_ignored.set( device.is_ignored.get() ) 

    def link(self, motor):
        for action in self.find( QtLinkedAction, -1):
            action.link(motor)
    
    def disconnect(self):
        if self._connection:
            self._connection.disconnect()

    def connect(self, device):
        self.link(device)
        # data_in = self.DataIn()
        # data_out = self.DataOut()
        
        self.name.set( device.name ) 
        
        if self.engine.connector:
            self._connection = self.engine.connector.new_connection()
            self._connection.add_nodes(  get_connection_pairs(self, device) )
            self._connection.add_callbacks( [self.refresh] )
        # self.move.link(motor)
        # self.stop.link(motor)
        # self.change_state.link(motor) 
        # self.move_by_name.link(motor)
        
class MainWidget(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.main_layout = QVBoxLayout()
        self.setLayout( self.main_layout ) 
        

class Main(QtDevice):
    motor = QtNodeFactory(widget=QComboBox, vtype=(str,"motor1"), items=["motor1", "motor2"],
            appender=ToLayout("main_layout"))

    class Config:
        devices: List[QtDevice.Config] = []
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.motor  
    def add_motor(self, motor):
        f = QtDeviceFactory( obj_type=Motor, kind="ctrl", appender=ToLayout("main_layout"))
        
        # self.devices.append( QtMotor.Config(  widget=QtMotorWidget(), appender=ToLayout("main_layout")) )
        self.devices.append(f) 
        self.devices[-1].connect(motor)   
    def pop_motor(self):
        dev = self.devices.pop()
        dev.kill()

if __name__ == "__main__":
    
    app = QApplication(sys.argv)
    # widget = QtMotorWidget()
    main  = Main(widget=MainWidget, connector=Connector())
    
    
    # m = QtMotor(widget=QtMotorWidget())
    # print( m.widget )
    

    # with Motor( address="opc.tcp://192.168.1.11:4840" , prefix="MAIN.Motor1") as motor:
    with open_elt_device("tins/motor1.yml(motor1)") as motor:
        with open_elt_device("tins/motor2.yml(motor2)") as motor2:
            main.add_motor(motor)

            # m = QtMotor(widget=QtMotorWidget(), origin=motor)
            

            # print( [(n1.name, n2.name) for n1,n2 in  m.stat.get_connection_pairs( motor.stat )] )
            # print( [(n1.name, n2.name) for n1,n2 in  m.get_connection_pairs( motor, implicit=None )] )


            timer = QtCore.QTimer()
            i = 0 
            def u():
                global i
                main.engine.connector.update()
                v.set(   len(main.engine.connector.downloader_connection._downloader._nodes) )
                i+=1
                if i==20:
                    main.add_motor(motor2)
                if i==40:
                    main.pop_motor()
                if i==60:
                    main.devices[0].disconnect()
                    main.devices[0].connect(motor2)
            timer.timeout.connect(u)#main.engine.connector.update)
            timer.start(200) 
            # m.widget.show() 
            main.widget.show()
            app.exec_()
    

