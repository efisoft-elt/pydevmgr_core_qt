from pydevmgr_core.base.base import BaseObject

from pydevmgr_core_qt.qt_objects.base import QtBase
from .engine import QtEngine, resolve_widget
from .interface import QtInterface 
from .node import QtNode 

from pydevmgr_core import BaseDevice 


class QtDevice(QtBase, BaseDevice):
    class Config(BaseDevice.Config, QtEngine.Config):
        pass 
    Engine = QtEngine
    Node = QtNode 
    Interface = QtInterface
  
