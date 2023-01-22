from typing import Type
from pydevmgr_core.base.base import BaseObject
from systemy.system import BaseFactory

from pydevmgr_core_qt.qt_objects.device import QtDevice
from pydantic import Extra



qtdevice_loockup = {}
def register_qtdevice(obj_type: Type[BaseObject], kind: str):
    def recorder(cls):
        qtdevice_loockup[(obj_type, kind)] = cls 
        return cls 
    return recorder 

def get_qtdevice_class(obj_type: Type[BaseObject], kind: str):
    try:
        return qtdevice_loockup[(obj_type, kind)]
    except KeyError:
        raise ValueError(f"QtDevice for object of type {obj_type} and kind {kind} cannot be found")
    

class QtDeviceFactory(BaseFactory):
    """ A factory for a QtDevice 

    The write QtDevice is iddentified by the pair of argument:
    - obj_type: The type of a pydevmgr object associated with the QtDevice 
    - kind (str): a string representing the kind of widget 

    The QtDevice class must have been registered by :func:`register_qtdevice`
    
    All extra keywords are parsed to the targeted QtDevice Factory 
    """
    obj_type: Type[BaseObject] 
    kind: str
    class Config:
        extra = Extra.allow 

    @classmethod
    def get_system_class(cls):
        return QtDevice

    def build(self, parent = None, name = None):
        QtDeviceClass = get_qtdevice_class( self.obj_type, self.kind)
        args = self.dict(exclude={"obj_type", "kind"})

        if "widget" not in args:
            args['widget'] = QtDeviceClass.get_widget_class()
        return QtDeviceClass.Config(**args).build(parent, name)
