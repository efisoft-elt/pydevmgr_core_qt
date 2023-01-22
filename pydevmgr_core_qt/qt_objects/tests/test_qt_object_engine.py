from pydevmgr_core_qt.qt_objects.engine import QtEngine, QtNodeEngine 

from PyQt5.QtWidgets import QApplication, QHBoxLayout, QWidget
from PyQt5 import QtCore
import sys

from pydevmgr_core_qt.qt_objects.path import WidgetName 

app = QApplication(sys.argv)


class MyWidget(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        layout = QHBoxLayout(self)
        self.sub_widget = QWidget()
        self.sub_widget.setObjectName("toto")
        layout.addWidget( self.sub_widget )


def test_engine():
    myw = MyWidget() 
    QtEngine( widget=myw )
    e = QtEngine.new( myw, QtEngine.Config(widget_prefix="sub_widget") )
    assert e.widget ==  myw.sub_widget
        
    e = QtEngine.new( myw, QtEngine.Config(widget_prefix=WidgetName("toto")) )
    assert e.widget ==  myw.sub_widget

def test_node_engine():
    myw = MyWidget()  
    engine = QtEngine( widget=myw )
    e = QtNodeEngine.new(  engine, QtNodeEngine.Config(widget="sub_widget")) 
    assert e.widget == myw.sub_widget
    
test_node_engine()
    
