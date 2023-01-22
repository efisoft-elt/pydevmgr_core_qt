from dataclasses import dataclass
from enum import Enum
from typing import Any, Optional, Type, Union
from pydevmgr_core import DataEngine, storedproperty
from pydevmgr_core.base.base import BaseObject
from pydevmgr_core.base.engine import BaseEngine
from pydevmgr_core.base.object_path import BasePath, PathVar
from PyQt5.QtWidgets import QLayout, QWidget
from pydevmgr_tools.api import BaseAppender

from pydevmgr_core_qt.qt_objects.connection import Connector


def handle_widget_without_parent(widget):
    # widget.show()
    return widget 

def handle_widget_with_parent(parent, widget, appender):
    if appender is None:
        raise ValueError("receive a new widget but do not know what to do, provide an appender")
    appender.append(parent, widget)
    return widget 

def resolve_widget(parent, widget, appender):
    if not widget:
        return parent 
    
    if isinstance( widget, type):
        if not issubclass(widget, QWidget):
            raise ValueError("got a type which is not a QWidget")
        widget = widget()

    if isinstance(widget, QWidget):
        if parent is None:
            return handle_widget_without_parent(widget)
        else:
            return handle_widget_with_parent(parent, widget, appender)
    
    if isinstance(widget, BasePath):
        if parent is None:
            raise ValueError("Didn't receive a parent widget")
        return widget.resolve(parent)
    
    raise ValueError("Bad argument for widget")


def new_opath(opath, origin):
    if origin is None:
        return None 
    if isinstance(origin, BaseObject):
        return origin
    # if isinstance(opath, BasePath):
    #     return opath.add( origin)
    return origin


class WidgetMaker:
    def __init__(self, WidgetType, **kwargs):
        self.WidgetType = WidgetType
        self.kwargs = kwargs 
    def __call__(self,*args,  **kwargs):
        return self.WidgetType(*args, **{**self.kwargs, **kwargs})




@dataclass
class WidgetPath:
    widget: QWidget
    parent: "WidgetPath" = None
    appender: Optional[BaseAppender] = None
    
    def __post_init__(self):
        self._resolved = None 
    
    def resolve(self):
        if self._resolved: return self._resolved 

        if self.parent:
            parent = self.parent.resolve() 
        else: 
            parent = None 
        widget = self.widget 
        
        if isinstance( widget, (type, WidgetMaker)):
            widget = widget()
        if isinstance( widget, QWidget):
            if parent:
                widget = handle_widget_with_parent(parent, widget, self.appender)
            else:
                widget = handle_widget_without_parent(widget)
        elif isinstance(widget, BasePath):
            widget = widget.resolve(parent)
        else:
            raise ValueError("cannot resolve any widget")
        self._resolved = widget 
        return self._resolved 
    
    def clear(self):
        self._resolved = None 
        
    def set_widget(self, widget):
        self.clear()
        self.widget = widget
        
@dataclass
class LinkPath:
    obj: Any 
    parent: Optional["LinkPath"]
        
    def __post_init__(self):
        self._resolved = False 
        self._resolved_obj = None 
    
    def resolve(self):
        if self._resolved: return self._resolved_obj 
        if self.parent:
            parent = self.parent.resolve() 
        else: 
            parent = None 
        obj = self.obj 
        if isinstance( obj, BaseObject):
            pass 
        elif isinstance( obj, BasePath):
            obj = obj.resolve(parent)
        self._resolved = True 
        self._resolved_obj = obj
        return obj  

    def clear(self):
        self._resolved = False 
        
    def set_object(self, obj):
        self.clear()
        self.obj = obj
        
  
         
class Implicit(str, Enum):
    none   = "none"
    origin = "origin"
    target = "target"
    both   = "both"
    never  = "never"

@dataclass
class QtEngine(DataEngine):
    connector: Optional[Connector] = None 
    wpath: Optional[WidgetPath] = None
    
    class Config(DataEngine.Config):
        widget: Optional[Union[Type[QWidget],QWidget,WidgetMaker,PathVar]] = None 
        appender: Optional[BaseAppender] = None
        connector: Optional[Union[Connector, Connector]] = None 
        origin: Optional[Union[BaseObject,PathVar]] = None      
        target: Optional[Union[BaseObject,PathVar]] = None 
        implicit: Optional[Implicit] = Implicit.none 

        class Config:
            arbitrary_types_allowed = True
    

    def clear(self):
        w = self.__dict__.pop("widget",None)
        self.wpath.clear()
        if w: w.setParent(None)

    @storedproperty  
    def widget(self):
        if not self.wpath: return 
        return self.wpath.resolve()    
    
        
    @classmethod
    def new(cls, com, config):
        
        if isinstance(com, QWidget):
            parent, com, connector = com, None, None
            wpath = WidgetPath(parent, parent=None, appender=config.appender)
        elif isinstance( com, QtEngine):
            connector = com.connector
            if config.widget:
                wpath = WidgetPath(config.widget, parent=com.wpath, appender=config.appender)
            else: 
                wpath = com.wpath 
            
        else:
            connector = None 
            wpath = WidgetPath( config.widget, parent=None, appender=config.appender)

        connector = config.connector or connector

        engine = super().new(com,config)
        engine.connector = connector 
        engine.wpath = wpath

        return engine


@dataclass
class QtNodeEngine(BaseEngine):
    widget: Optional[None] = None 
    class Config(BaseEngine.Config):
        widget: Union[QWidget, PathVar] 
        class Config:
            arbitrary_types_allowed = True
    
    @classmethod
    def new(cls, com, config):
        widget = None  
        if com is None:
            widget = None 
        elif isinstance(com, QWidget):
            com, widget = None, com 
        elif not isinstance( com, QtEngine):
            widget, com = None, com 
        else:
            widget = com.widget 

        engine = super().new(com, config)
        
        if isinstance( config.widget, BasePath):
            if widget is None:
                raise ValueError( "QtNodeEngine didn't receive a root widget")
            widget = config.widget.resolve(widget)
        elif isinstance(config.widget, QWidget):
            widget = config.widget 
    
        engine.widget = widget 
        return engine 


      


