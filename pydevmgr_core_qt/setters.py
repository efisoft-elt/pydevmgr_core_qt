


from dataclasses import dataclass, field
from enum import Enum, EnumMeta
from typing import Callable, Optional, Any, Type

from PyQt5.QtWidgets import QCheckBox, QFrame, QLabel, QMainWindow, QWidget
from PyQt5 import QtWidgets

from valueparser import BaseParser, parser
from pydevmgr_core_qt.getters import QtBoolTextGetter, QtTextGetter
from pydevmgr_core_qt.style import Style, get_style

from pydevmgr_tools.setter import BaseSetter, get_setter_class as get_class ,  register_setter as register 
from pydevmgr_tools.feedback import BaseContainerFeedback
from typing import Tuple 
from pydantic import BaseModel


__all__ = [
"QtTextSetter",
"QtFloatSetter", 
"QtIntSetter", 
"QtBoolSetter", 
"QtCheckSetter", 
"QtComboEnumSetter", 
"QtIo", 
"QtIoSetter",
"IoGroup",
"QtLabelEnumSetter", 
"QtStyleSwitcher", 
"QtTextSetter", 
"QtComboStrSetter"
]



@register("QLineEdit", "str")
@register(QtWidgets.QLineEdit, str)
@register(QtWidgets.QLabel, str)
@dataclass
class QtTextSetter(BaseSetter):
    """ A setter for any QT widget with setText() method """
    format: str = "%s"
    parser: Optional[BaseParser] = None
    feedback: Optional[BaseContainerFeedback] =None
    def __post_init__(self):
        if self.parser:
            self.parser = parser(self.parser)
        
    def set(self, widget, value) -> None:
        if self.feedback:
            try:
                value = self.parse(value)
            except Exception as err:
                self.feedback.error(widget, err)
                return 
            else:
                self.feedback.clear(widget, self.format % value)
        else:
            value = self.parse(value)
        
        widget.setText(self.format % value)
    
    def parse(self, value):
        if not self.parser: return value
        return self.parser.parse(value)



@register(QtWidgets.QLineEdit, float)
@register(QtWidgets.QLabel, float)
@dataclass
class QtFloatSetter(QtTextSetter):
    format: str = "%f"
    parser: BaseParser = parser(float)

@register(QtWidgets.QLineEdit, int)
@register(QtWidgets.QLabel, int)
@dataclass
class QtIntSetter(QtTextSetter):
    format: str = "%d"
    parser: BaseParser = parser(int)



@register(QtWidgets.QLineEdit, bool)
@register(QtWidgets.QLabel, bool)
@dataclass
class QtBoolSetter(BaseSetter):
    true_text: str = "[X]"
    false_text: str = "[ ]"
    reverse: bool = False 
    def set( self, widget, value) -> None:
        value = bool(value)
        if self.reverse:
            value = not value
        if isinstance(widget, QCheckBox):
            widget.setChecked(value)
        else:
            widget.setText( self.true_text if value else self.false_text )

@register(QtWidgets.QCheckBox, bool)
@dataclass
class QtCheckSetter(BaseSetter):
    reverse: bool = False
    def set( self, widget: QCheckBox, test: bool) -> None:
        test = bool(test)
        if self.reverse:
            test = not test 
        widget.setChecked( test )


@register(QtWidgets.QComboBox, EnumMeta)
@register(QtWidgets.QComboBox, Enum)
@dataclass
class QtComboEnumSetter(BaseSetter):
    enum: Enum
    offset: int = 0 
    def set(self, widget, value):
        value = self.enum(value)
        index = list(self.enum).index(value)
        widget.setCurrentIndex( index + self.offset)


@register(QtWidgets.QComboBox, str)
@dataclass
class QtComboStrSetter(BaseSetter):
    offset: int = 0 
    def set(self, widget, value):
        index = widget.findText(value)
        if index>=0:
            widget.setCurrentIndex( index)

@register(QtWidgets.QLabel, EnumMeta)
@register(QtWidgets.QLabel, Enum)
@dataclass
class QtLabelEnumSetter(BaseSetter):
    enum: Enum
    def set(self, widget, value):
        value = self.enum(value)
        widget.setText( value.name )




@dataclass
class QtStyleSwitcher(BaseSetter):
    true_style: str = get_style(Style.SIMILAR)
    false_style: str = get_style(Style.DIFFERENT)
    def set(self, widget: QWidget, test: bool) -> None:
        widget.setStyleSheet( self.true_style if test else self.false_style )


@dataclass
class QtIoSetter(BaseSetter):
    setter: QtTextSetter = QtTextSetter()
    getter: QtTextGetter = QtTextGetter()
    style_switcher: QtStyleSwitcher = QtStyleSwitcher()
    comparator: Callable = lambda x,y: x==y  

    def set(self, widgets: Tuple[QWidget, QWidget],  value) -> None:
        input, output = widgets
        self.setter.set(output, value)
        test = self.comparator(value, self.getter.get(input) )
        self.style_switcher.set(output, test)

    def get(self, widgets: Tuple[QWidget, QWidget]):
        input, _ = widgets
        return self.getter.get(input)
    
    def set_input(self, widgets: Tuple[QWidget, QWidget], value: Any) -> None:
        input, _ = widgets
        self.setter(input, value)


@dataclass
class IoGroup:
    input: Any
    output: Any 
    def __iter__(self):
        yield self.input 
        yield self.output

@dataclass
class QtIo(BaseSetter):
    setter: QtTextSetter = QtTextSetter()
    getter: QtTextGetter = QtTextGetter()
    style_switcher: QtStyleSwitcher = QtStyleSwitcher()
    comparator: Callable = lambda x,y: x==y  

    def set(self, widgets: IoGroup,  value) -> None:
        input, output = widgets.input, widgets.output
        
        self.setter.set(output, value)
        test = self.comparator(value, self.getter.get(input) )
        self.style_switcher.set(output, test)

    def get(self, widgets: IoGroup):
        return self.getter.get(widgets.input)
    
    def set_input(self, widgets: IoGroup, value: Any) -> None:
        self.setter(widgets.input, value)

if __name__ == "__main__":
    class E(Enum):
        a = 0
    get_class(QtWidgets.QLabel, type(E))
