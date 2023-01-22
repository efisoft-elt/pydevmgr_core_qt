from PyQt5.QtWidgets import QWidget
from pydevmgr_core.base.object_path import BasePath , DummyPath, objpath

class WidgetName(BasePath):
    def __init__(self, name: str, Type=QWidget):
        self._name = name 
        self._type = Type
    def resolve(self, root:QWidget) -> QWidget:
        return root.findChild( self._type, self._name) 
    def split(self):
        return DummyPath(), self 
    def set_value(self, root, widget):
        raise ValueError("Cannot set a widget from WidgetPath")


class WidgetGroup:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

class WidgetGroupPath(BasePath):
    def __init__(self,  Type=WidgetGroup, **path):
        self._path = {k: objpath(p) for k,p in path.items()}
        self._Type= Type
    def resolve(self, root):
        return self._Type( **{k:p.resolve(root) for k,p in self._path.items()} )  

