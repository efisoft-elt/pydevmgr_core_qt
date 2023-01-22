from typing import Any, Optional, Type, Union
from PyQt5.QtWidgets import QWidget
from pydevmgr_core import BaseNode
from pydevmgr_core.base.object_path import PathVar
from pydevmgr_core.base.vtype import VType, nodetype
from pydevmgr_tools.builder import BaseBuilder, get_builder_class
from pydevmgr_tools.getter import BaseGetter, get_getter_class
from pydevmgr_tools.setter import BaseSetter, get_setter_class
from systemy.system import BaseFactory
from pydevmgr_core_qt.qt_objects.base import QtBase
from pydevmgr_core_qt.qt_objects.engine import QtEngine, QtNodeEngine 
from pydevmgr_core_qt.qt_objects.widget_var import WidgetVar 

from enum import Enum, EnumMeta 
import inspect 






class QtNode(QtBase, BaseNode):
    Engine = QtEngine 

    class Config(BaseNode.Config, QtEngine.Config):
        getter : Optional[BaseGetter] = None 
        setter : Optional[BaseSetter] = None
        builder: Optional[BaseBuilder] = None
        
        class Config:
            arbitrary_type_allowed = True
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.builder:
            self.builder.build(self.engine.widget)
    
    def fget(self):
        return self.getter.get(self.engine.widget) 
        
    def fset(self, value):
        self.setter.set(self.engine.widget, value)

 
