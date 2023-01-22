

import sys
from PyQt5 import QtCore
from PyQt5.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget
from pydevmgr_core.base.base import find_factories
from pydevmgr_core.base.node import BaseNode
from pydevmgr_core.base.object_path import objpath
from pydevmgr_core.base.vtype import nodetype
from pydevmgr_elt.base.eltdevice import open_elt_device
from pydevmgr_elt.devices.motor import Motor
from systemy.system import FactoryDict
from pydevmgr_core_qt.appenders import ToLayout
from pydevmgr_core_qt.elements import QValueLabel
from pydevmgr_core_qt.qt_objects.base import get_connection_pairs
from pydevmgr_core_qt.qt_objects.connection import  Connector
from pydevmgr_core_qt.qt_objects.device import QtDevice

from pydevmgr_core_qt.qt_objects.node_factory import QtNodeFactory


args = {}
for attr, factory in find_factories( Motor.Cfg, BaseNode):
    if nodetype(factory) in [float, int]:
        if not attr.startswith("init"):
            args[attr] = QtNodeFactory( vtype=nodetype(factory), widget=QValueLabel, origin=attr,
                    appender=ToLayout("main_layout"), label=attr)



class Cfg(QtDevice):
    
    nodes = FactoryDict( args )

    def connect_to(self, device):
        nodes = self.get_connection_pairs(device)
         
        if self.engine.connector:
            self._connection = self.engine.connector.new_connection()
            self._connection.add_nodes( nodes )

if __name__ == "__main__":
    app = QApplication(sys.argv)

    widget = QWidget()
    layout = QVBoxLayout()
    widget.setLayout( layout)
    widget.main_layout = layout 
    
    with open_elt_device("tins/motor1.yml(motor1)") as motor:
        cfg = Cfg( widget =widget , connector = Connector() )

        cfg.connect_to( motor.cfg) 
        timer = QtCore.QTimer()
        timer.timeout.connect(cfg.engine.connector.update)#main.engine.connector.update)
        timer.start(200) 
        # m.widget.show() 
        widget.show()
        app.exec_()

