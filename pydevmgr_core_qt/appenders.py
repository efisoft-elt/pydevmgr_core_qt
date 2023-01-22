from dataclasses import dataclass
from typing import Union
from PyQt5.QtWidgets import QLayout, QWidget
from pydevmgr_core.base.object_path import PathVar
from pydevmgr_tools.api import BaseAppender


__all__ = [
    "ToLayout"
]


@dataclass
class ToLayout(BaseAppender):
    layout: Union[PathVar, str, QLayout]

    def append(self, parent: QWidget, widget: QWidget)->None:
        if isinstance(self.layout, QLayout):
            layout = self.layout 
        else:
            if parent is None:
                raise ValueError(f"Received a new widget to append to {self.layout!r} but parent is None")
            layout = PathVar(self.layout).resolve(parent) 
        
        layout.addWidget( widget )
        
