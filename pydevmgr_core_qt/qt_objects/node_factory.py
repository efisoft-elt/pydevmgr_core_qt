from enum import Enum, EnumMeta
import inspect
from typing import Optional, Type, Union
from PyQt5.QtWidgets import QWidget
from pydantic.main import BaseModel
from pydevmgr_core.base.object_path import PathVar
from pydevmgr_core.base.vtype import VType, nodetype
from pydevmgr_tools.builder import get_builder_class
from pydevmgr_tools.getter import get_getter_class
from pydevmgr_tools.setter import get_setter_class
from systemy import BaseFactory
from pydevmgr_core_qt.qt_objects.engine import QtEngine, WidgetMaker

from pydevmgr_core_qt.qt_objects.node import QtNode
from pydevmgr_core_qt.qt_objects.widget_var import WidgetVar 
from warnings import warn 


class QtNodeMode(str, Enum):
    G = "g"
    S = "s"
    GS = "gs"


def iter_fields(cls):
    """ iterate fields of the data class """
    if isinstance(cls, BaseModel):
        return iter(cls.__fields__)
    return cls.__dataclass_fields__


def extract_kwargs(cls, model, unused):
    kwargs =  {}
    for f in iter_fields(cls):
        if f in model.__dict__:
            kwargs[f] = getattr( model, f)
            try:
                unused.remove(f)
            except KeyError:
                pass 
    return kwargs

def init_takes_one_positional_argument(cls):
    signature = inspect.signature(cls.__init__)
    if len(signature.parameters)>1:
        params = list(signature.parameters)
        arg1 = signature.parameters[params[1]]
        if arg1.kind == arg1.POSITIONAL_ONLY:
            return True 
        elif arg1.kind == arg1.POSITIONAL_OR_KEYWORD and arg1.default is inspect._empty:
            return True 
    return False


def initialise_helpers(cls, model, unused):
    kwargs = extract_kwargs( cls, model, unused)
    if init_takes_one_positional_argument(cls):
        return cls(nodetype(model), **kwargs)
    return cls(**kwargs)


def get_type(model):
    type_ = nodetype(model)
    if isinstance(type_, EnumMeta):
        return Enum #type(type_)
    else:
        return type_

def guess_getter(Widget, model, unused):
    cls =  get_getter_class( Widget, get_type(model))
    return initialise_helpers(cls, model, unused)

def guess_setter(Widget, model, unused):
    cls =  get_setter_class( Widget , get_type(model))
    return initialise_helpers(cls, model, unused)

def guess_builder(Widget, model, unused):
    cls =  get_builder_class( Widget, get_type(model))
    return initialise_helpers(cls, model, unused)


def get_widget_class(parent, widget):
    if isinstance( widget, QWidget):
        return widget.__class__ 
    if isinstance( widget, type):
        return widget
    if isinstance( widget, WidgetMaker):
        return widget.WidgetType
    
    else:
        if parent is None:
            raise ValueError("Cannot build QtNode without a parent class")
        return widget.resolve(parent.engine.widget).__class__
        


class QtNodeFactory(BaseFactory, QtEngine.Config):
    vtype: Optional[VType] = str 
    mode : QtNodeMode = QtNodeMode.GS 
    class Config:
        extra = "allow"
    @classmethod
    def get_system_class(cls):
        return QtNode 

    def build(self, parent=None, name=None):
        
        Widget = get_widget_class(parent, self.widget)
        # widget = parent.engine.new(parent.engine,self).widget

        unused = { k for k in self.__dict__ if k not in self.__fields__}
        
        getter = guess_getter(Widget, self, unused) if "g" in self.mode else None 
        setter = guess_setter(Widget, self, unused) if "s" in self.mode else None 
        try:
            builder = guess_builder(Widget, self, unused)
        except ValueError:
            builder = None 

        
        if unused:
            warn( f"The following parameters are not used: {unused!r} ")
        
        cls = self.get_system_class()

        args = self.dict( include=set( cls.Config.__fields__) ) 
        if parent is None:
            return cls( **args, layout=self.layout, getter=getter, setter=setter, builder=builder)
        else:
            return cls.new(parent, name, 
                    cls.Config(  **args,   
                                    getter=getter,
                                    setter=setter,
                                    builder=builder
                        )
                    )
    
if __name__ == "__main__":
    
   pass 
