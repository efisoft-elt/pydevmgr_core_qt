from PyQt5.uic.uiparser import QtWidgets
from pydantic.main import BaseModel
from pydevmgr_core import BaseMonitor, BaseObject
from pydevmgr_tools.api import BaseConnector
from PyQt5.QtWidgets import  QWidget



qt_loockup = {}
def register_qt( object_type, kind):
    """ recorder for a new ui class for an object type and ui kind 

    Args:
        object_type: a valid pydevmgr BaseObject :class:`pydevmgr_core.BaseDevice`
        kind: str widget kind for the guiven object 
    
    """
    def record(cls):
        qt_loockup[( kind, object_type)] = cls
        return cls
    return record

def get_qt_class( object_type, kind, default=None):
    """ Return an UI class for the given object and kind 

     Args:
        object_type: a valid pydevmgr BaseObject :class:`pydevmgr_core.BaseDevice`
        kind: str widget kind for the guiven object 
  
    """

    try:
        return qt_loockup[( kind, object_type)]
    except KeyError:
        if default is None:
            raise ValueError(f"Cannot find a ui handler for kind={kind} and device type={object_type}") 
        else:
            return default 


class QtMonitor(BaseMonitor):
    def setup(self, widget:QWidget, data: BaseModel, obj:BaseObject):
        pass
    
    def start(self, widget:QWidget, data: BaseModel):
        pass

    def error(self, widget: QWidget, err: Exception):
        widget.setEnabled(False)
        print( err)
    
    def clear_error(self, widget: QWidget):
         widget.setEnable(True)
    
    def update(self, widget: QWidget, data: BaseModel):
        pass
    
    def stop(self, widget: QWidget):
        pass
    

class BaseRemover:
    def remove(self, widget: QWidget):
        raise NotImplementedError("remove")




         


