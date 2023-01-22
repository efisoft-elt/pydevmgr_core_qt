from pydevmgr_core_qt.qt_objects.base import QtBase
from .engine import QtEngine
from .node import QtNode 
from pydevmgr_core import BaseInterface  


class QtInterface(QtBase, BaseInterface):
    class Config(BaseInterface.Config, QtEngine.Config):
        pass 
    Engine = QtEngine
    Node = QtNode 
    

