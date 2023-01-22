from dataclasses import dataclass, field
from pydevmgr_tools.builder import BaseBuilder, register_builder as register, get_builder_class as get_class 
from PyQt5 import QtWidgets
from enum import EnumMeta, Enum


__all__ = [
"QtComboEnumBuilder", 
"QtComboListBuilder", 
"QtComboDictBuilder"
]

@register(QtWidgets.QComboBox, Enum)
@register(QtWidgets.QComboBox, EnumMeta)
@dataclass
class QtComboEnumBuilder(BaseBuilder):
    """ Setup a QtComboBox from an Enumerator """
    enum: EnumMeta
    clear: int = False
    def build(self, widget):
        if self.clear:
            widget.clear()
        for e in self.enum:
            name = str(e.name)
            if name == "_": name=""
            widget.addItem( name, e )

@register(QtWidgets.QComboBox, str)
@dataclass
class QtComboListBuilder(BaseBuilder):
    """ Setup a QtComboBox from an Enumerator """
    items: list = field(default_factory=list)
    clear: int = False
    def build(self, widget):
        if self.clear:
            widget.clear()
        for item in self.items:
            widget.addItem( str(item) )


@register(QtWidgets.QComboBox, list)
@dataclass
class QtComboDictBuilder(BaseBuilder):
    """ Setup a QtComboBox from an Enumerator """
    data: list = field(default_factory=dict)
    clear: int = False
    def build(self, widget):
        if self.clear:
            widget.clear()
        for item, value in self.data.items():
            widget.addItem( str(item), value )

        

