
from typing import Generic, TypeVar
from PyQt5.QtWidgets import QWidget
from pydantic.error_wrappers import ValidationError

from pydantic.fields import ModelField


WidgetType = TypeVar('WidgetType')

class WidgetVar(Generic[WidgetType]):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate
    @classmethod
    def __modify_schema__(cls, field_schema):
        pass 
    
    @classmethod
    def validate(cls, v, field: ModelField):
        if field.sub_fields:
            raise ValidationError(['WidgetVar does not accept sub-fields'], cls)
        
        if isinstance( v, QWidget):
            return v 
        raise ValidationError([f'{type(v)} is not a QWidget'], cls)

    
    def __repr__(self):
        return f'{self.__class__.__name__}({super().__repr__()})'


