from typing import Optional
from pydevmgr_core.base.base import BaseObject, ParentWeakRef
from pydevmgr_core.base.vtype import VType
from pydevmgr_tools.action import Action
from pydevmgr_tools.connector import BaseConnector, get_connector_class
from pydevmgr_core_qt.qt_objects.base import QtBase

from pydevmgr_core_qt.qt_objects.engine import QtEngine, QtNodeEngine


class QtLinkedAction(ParentWeakRef,QtBase, BaseObject):
    """ An action which will be linked to a device 

    The action is settled when .link(device) is called
    The action is automatically linked to the self.widget object if 
    a connector is found or given
    """
    Engine = QtEngine
    class Config(BaseObject.Config, QtEngine.Config):
        connector: None = None
        class Config:
            arbitrary_type_allowed = True
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._actions = []
      
    def link(self, device: BaseObject)-> None:
        raise NotImplementedError('link')
   
    def set_action(self, action: Action):
        if action in self._actions:
            return 
        connector = self.connector 

        if connector is None:
            connector = get_connector_class(self.widget.__class__, action.__class__)() 

        self._actions.append(action) # necessary to save it (weakref somewhere)
        connector.connect(self.widget, action)

    def trigger(self):
        for action in self._actions:
            action.trigger()

class QtStandAloneAction(ParentWeakRef,QtBase, BaseObject):
    """ An stand alone action 

    The action is settled when .link() is called
    The action is automatically linked to the self.widget object if 
    a connector is found or given
    """
    Engine = QtEngine
    class Config(BaseObject.Config, QtEngine.Config):
        connector: None = None
        class Config:
            arbitrary_type_allowed = True
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._actions = []
      
    def link(self)-> None:
        raise NotImplementedError('link')
    
    def set_action(self, action: Action):
        if action in self._actions:
            return 
        connector = self.connector 

        if connector is None:
            connector = get_connector_class(self.widget.__class__, action.__class__)() 

        self._actions.append(action) # necessary to save it (weakref somewhere)
        connector.connect(self.widget, action)

    def trigger(self):
        for action in self._actions:
            action.trigger()

