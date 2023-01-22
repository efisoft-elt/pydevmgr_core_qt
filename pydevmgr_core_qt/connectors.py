from typing import Dict, Optional

from PyQt5.QtWidgets import QAction, QCheckBox, QPushButton, QWidget, QComboBox 
from pydevmgr_tools.action import ActionMap,  ActionIndex, Action, ActionEnum
from pydevmgr_tools.connector import register_connector as register, get_connector_class as get_class, BaseConnector 


__all__ = [
"QtActionMenuConnector", 
"QtButtonConnector", 
"QtCheckBoxConnector", 
"QtComboConnector", 
"QtComboIndexConnector"
]

@register(QComboBox, ActionIndex)
class QtComboIndexConnector(BaseConnector):
    """ Helper function to link some actions to a QT Combo box 

    Args:
        widget: :class:`PyQt5.QtWidgets.QComboBox`
        actions: :class:`ActionsIndex`
    
    """
    def connect(self, widget: QComboBox, actions: Action):
        widget.currentIndexChanged.connect(actions.trigger) 
    
    def add_item(self, widget, item, action: Optional[Action] = None):
        widget.addItem(item)
        if action: self.actions.add_action(  widget.count()-1, action)
    
    def disconnect(self, widget):
        widget.currentIndexChanged.disconnect()

@register(QComboBox, ActionMap)
class QtComboConnector(BaseConnector):
    """ Helper function to link some actions to a QT Combo box 
    
    Actions map and combo box item are matched by name. 
    The action is triggered when the selected item text is equal 
    to the action map keys.

    Args:
        widget: :class:`PyQt5.QtWidgets.QComboBox`
        actions: :class:`ActionsMap`
    
    """
    def connect(self, widget: QComboBox, actions: ActionMap):
        def callback(index):
            actions.trigger( widget.itemText(index) )
        widget.currentIndexChanged.connect(callback) 
    
    def add_item(self, widget, item, action:Optional[Action] = None):
        widget.addItem(item)
        if action: self.actions.add_action( item, action )
    
    def disconnect(self, widget):
        widget.currentIndexChanged.disconnect()



@register(QComboBox, ActionEnum)
class QtComboDataConnector(BaseConnector):
    """ Helper function to link some actions to a QT Combo box 
    
    Actions map and combo box item are matched by name. 
    The action is triggered when the selected item text is equal 
    to the action map keys.

    Args:
        widget: :class:`PyQt5.QtWidgets.QComboBox`
        actions: :class:`ActionsMap`
    
    """
    def connect(self, widget: QComboBox, actions: ActionMap):
        def callback(index):
            actions.trigger( widget.itemData(index) )
        widget.currentIndexChanged.connect(callback) 
    
    def add_item(self, widget, item, action:Optional[Action] = None):
        widget.addItem(str(item.name), item )
        if action: self.actions.add_action( item, action )
    
    def disconnect(self, widget):
        widget.currentIndexChanged.disconnect()



    
@register(QCheckBox, Action)
class QtCheckBoxConnector(BaseConnector):
    def connect(self, widget: QCheckBox, action: Action):
        widget.stateChanged.connect(action.trigger)

    def disconnect(self, widget: QCheckBox):
        widget.stateChanged.disconnect()
    
    
@register(QPushButton, Action)     
class QtButtonConnector(BaseConnector):
    def connect(self, widget: QPushButton, action: Action):
        widget.clicked.connect(action.trigger)

    def disconnect(self, widget: QCheckBox):
        widget.clicked.disconnect()
    

@register(QAction, Action)   
class QtActionMenuConnector(BaseConnector):
    def connect(self, qaction: QAction, action: Action):
        qaction.triggered.connect(action.trigger)

    def disconnect(self, qaction: QAction):
        qaction.triggered.disconnect()




