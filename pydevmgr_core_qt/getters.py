


from dataclasses import dataclass, field
import math
from typing import Any, List, Optional, Type
from PyQt5 import QtWidgets 
from PyQt5.QtWidgets import QCheckBox, QComboBox, QFrame, QMainWindow, QWidget
from pydantic.main import BaseModel

from pydevmgr_tools.getter import  BaseGetter, register_getter as register , get_getter_class as get_class
from pydevmgr_tools.feedback import BaseContainerFeedback

from valueparser import BaseParser, parser
from enum import Enum, EnumMeta

__all__ = [
"QtBoolCheckBoxGetter", 
"QtBoolTextGetter", 
"QtComboEnumGetter", 
"QtFloatGetter", 
"QtIntGetter", 
"QtTextGetter",
"QtComboStrGetter"
]

@register(QtWidgets.QLineEdit, str) 
@register(QtWidgets.QLabel, str) 
@dataclass
class QtTextGetter(BaseGetter):
    """ Getter for a Qt Object with a text() attribute (QLineEdit, QLabel) """
    parser: Optional[BaseParser] = None
    feedback: Optional[BaseContainerFeedback] = None
    def __post_init__(self):
        if self.parser:
            self.parser = parser(self.parser)
    
    def get(self, widget: QWidget):
        value = widget.text()
        if self.parser:
            try: 
                value = self.parser.parse(value)
            except Exception as er:
                if self.feedback:
                   self.feedback.error(widget, er) 
                raise er # error should be raised anyway 
            else:
                if self.feedback:
                    self.feedback.clear(widget, "") 
        return value 



@register(QtWidgets.QLineEdit, float) 
@register(QtWidgets.QLabel, float) 
@dataclass
class QtFloatGetter(QtTextGetter):
    """ A getter for QT object with .text() attribute which always return a float """
    parser: Optional[BaseParser] = parser(float)
    nan: bool = False
    def get(self, widget: QWidget):
        try:
            return super().get( widget) 
        except ValueError as er:
            if self.nan:
                return math.nan 
            raise er
 


@register(QtWidgets.QLineEdit, int) 
@register(QtWidgets.QLabel, int) 
@dataclass
class QtIntGetter(QtFloatGetter):
    """ A getter for QT object with .text() attribute which always return a int """
    parser: Optional[BaseParser] = parser(int)


@register(QtWidgets.QLineEdit, bool) 
@register(QtWidgets.QLabel,  bool)    
@dataclass
class QtBoolTextGetter(BaseGetter):
    """ A getter for QT object with .text() attribute which always return a int """
    true_texts:  List = field( default_factory= ["[X]", "1", "true", "True"].copy)
    false_texts: Optional[List] = None  #field( default_factory=["[ ]", "0", "false", "False", ""]) 
    feedback: Optional[BaseContainerFeedback] = None
    reverse: bool = False 
    
    def get(self, widget: QWidget):
        test = self._get(widget)
        if self.reverse:
            return not test 
        return test  
    def _get(self,  widget: QWidget)-> bool:
        text = widget.text().strip()
        if self.false_texts is None:
            if self.feedback: self.feedback.clear(widget, "")
            return text in self.true_texts
        else:
            if text in self.true_texts:
                if self.feedback: self.feedback.clear(widget, "")
                return True
            elif text in self.false_texts:
                if self.feedback: self.feedback.clear(widget, "")
                return False
            er = ValueError(f"{text!r} is neaser true or false")
            if self.feedback:
                self.feedback.error(widget, er) 
            raise er  

@register(QtWidgets.QCheckBox, bool)
@dataclass
class QtBoolCheckBoxGetter(BaseGetter):
    """ a getter for QCheckBox """
    reverse: bool = False 
    def get(self, widget: QCheckBox):
        test = widget.isChecked()
        if self.reverse:
            return not test 
        return  test 


class _EmptyDefault:
    pass
@register(QtWidgets.QComboBox, Enum)
@register(QtWidgets.QComboBox, EnumMeta)
@dataclass
class QtComboEnumGetter(BaseGetter):
    """ A getter class for a QComboBox """
    enum: Enum
    default: Any = _EmptyDefault 
    def get(self, widget :QComboBox):
        index = widget.currentIndex()
        member = widget.itemText(index)
        try:
            val = getattr( self.enum, member)
        except AttributeError:
            if self.default == _EmptyDefault:
                raise ValueError(f" item {member} is not a member of {self.enum}")
            else:
                val = self.default
        return val      



@register(QtWidgets.QComboBox, str)
@dataclass
class QtComboStrGetter(BaseGetter):
    """ A getter class for a QComboBox """
    def get(self, widget :QComboBox):
        index = widget.currentIndex()
        return widget.itemText(index)
