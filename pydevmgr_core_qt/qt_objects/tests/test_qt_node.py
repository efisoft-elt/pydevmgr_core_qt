
from enum import Enum
import sys
from PyQt5 import QtCore
from PyQt5.QtWidgets import QApplication, QCheckBox, QComboBox, QLineEdit, QPushButton, QVBoxLayout, QWidget, QLabel
from pydevmgr_core.base.base import find_factories
from pydevmgr_core.base.dataclass import create_data_model, set_data_model
from pydevmgr_core.base.datamodel import DataLink
from pydevmgr_tools.action import Action
from valueparser.parsers import Bounded, Clipped
from pydevmgr_core_qt import feedbacks
from pydevmgr_core_qt.builders import QtComboEnumBuilder
from pydevmgr_core_qt.getters import QtComboEnumGetter
from pydevmgr_core_qt.qt_objects.node import QtNode
from pydevmgr_core_qt.qt_objects.node_factory import QtNodeFactory

from pydevmgr_core_qt.qt_objects.device import QtDevice
from pydevmgr_core_qt.qt_objects.path import WidgetName
from pydevmgr_core_qt.setters import QtComboEnumSetter, QtFloatSetter, QtIntSetter, QtLabelEnumSetter


app = QApplication(sys.argv) 

def test_qt_node_getter():
    class Q:
        l = QLineEdit() 
    node = QtNode( vtype=str, widget=Q.l)



if __name__ == "__main__":
    
    class E(Enum):
        A = "A"
        B = "B"
        C = "C"
    
    


    main = QWidget()
    layout= QVBoxLayout(main)
    main.line1 =  QLabel()
    main.line1.setObjectName( "the_line1")
    main.line2 =  QLineEdit()

    main.combo1 = QComboBox()
    main.label1 = QLabel()
    main.label2 = QCheckBox()
    
    main.line3 =  QLabel()
    main.button1 = QPushButton()
    
    layout.addWidget(main.line1)
    layout.addWidget(main.line2)

    layout.addWidget(main.line3)
    layout.addWidget(main.combo1)
    layout.addWidget(main.label1)
    layout.addWidget(main.label2)
    layout.addWidget(main.button1)
    
    @set_data_model
    class Device(QtDevice):
        index  = QtNodeFactory( vtype=int, widget=WidgetName("the_line1") , format="%04d", parser=Bounded(max=20) )
        label  = QtNodeFactory( vtype=(E,E.A), mode="s", widget="label1")
        check  = QtNodeFactory( vtype=bool, widget="label2") 
        error = QtNodeFactory( vtype=str, widget="line3") 

    @set_data_model
    class DeviceIn(QtDevice):
        value = QtNodeFactory( vtype=float, parser=float, widget="line2",
                feedback=feedbacks.QtChangeStyleContainerFeedback()
                )
        
        abc    = QtNodeFactory( vtype=(E,E.A), widget="combo1")
    
    Data = create_data_model( "Data",  ( (a,f) for a,f in find_factories( Device) if a!="error"))
    
    dev = Device(com=main)
    devin = DeviceIn(com=main)
    


    d = Data() 
    dl = DataLink(dev, d) 
    

     
    def seti(value, e):
        print(value, e)
        dev.index.set(d.index+value)
        dev.label.set(e)
        d.index += value
        d.label = e

    act = Action( seti, [devin.value, devin.abc], feedback=feedbacks.QtTextFeedback( dev.error)  )
    main.button1.clicked.connect(act.trigger)  

    def update():
        # d.abc = E.B 
        d.check = not d.check 
        dl.upload()
    update() 

    timer = QtCore.QTimer()
    timer.timeout.connect(update)
    timer.start(2000) 
    main.show()
    app.exec_() 
