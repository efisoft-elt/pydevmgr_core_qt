
from typing import List, Optional, Tuple, Union

from pydevmgr_core import BaseNode, ObjPath
from pydevmgr_core.base.base import BaseObject
from pydevmgr_core.base.object_path import objpath
from systemy.system import SystemDict, SystemList
from .engine import Implicit 

def _collect_origin_node_pairs(
        nodes: List[Tuple[BaseNode, BaseNode]], 
        qtobj: "QtBase",
        origin: BaseObject, 
        implicit = None, 
    )-> None:

    if isinstance( qtobj, QtBase):
        true_origin = qtobj.resolve_origin(origin, implicit)

        if isinstance( qtobj, BaseNode):
            if true_origin:
                nodes.append( (true_origin, qtobj) )

        if implicit is None:
            if qtobj.implicit in [Implicit.both, Implicit.origin]:
                implicit = True 
        if qtobj.implicit is Implicit.never:
            implicit = False

           
    else:
        true_origin = origin
    
    for child in qtobj.find( (BaseObject,SystemDict,SystemList) ):
            _collect_origin_node_pairs(nodes, child, true_origin or origin, implicit)

def _collect_target_node_pairs(
        nodes: List[Tuple[BaseNode, BaseNode]], 
        qtobj: "QtBase",
        target: BaseObject, 
        implicit = None, 
    )-> None:

    if isinstance( qtobj, QtBase):
        true_target = qtobj.resolve_target(target, implicit)

        if isinstance( qtobj, BaseNode):
            if true_target:
                nodes.append( (qtobj, true_target) )

        if implicit is None:
            if qtobj.implicit in [Implicit.both, Implicit.target]:
                implicit = True 
        if qtobj.implicit is Implicit.never:
            implicit = False

           
    else:
        true_target = target
    
    for child in qtobj.find( (BaseObject,SystemDict,SystemList) ):
            _collect_target_node_pairs(nodes, child, true_target or target, implicit)

  
def _get_origin_and_target_implicit_flags(implicit: Implicit)-> Tuple[bool, bool]:
        if implicit is Implicit.never:
            return False, False 
        if implicit is Implicit.both: 
            return True, True 
        if implicit in Implicit.origin:
            return True, None 
        if implicit in Implicit.target:
            return None, True 
        return None, None


def get_connection_pairs(
      obj_a: Union[BaseObject, SystemList, SystemDict], 
      obj_b: Union[BaseObject, SystemList, SystemDict], 
      implicit: Implicit = Implicit.none
) -> List[Tuple[BaseNode, BaseNode]]:
    """ From a pydevmgr object and a QtBase return nodes pairs for connection 
    
    It is expected that obj_a (first argument) has QtBase object which define
    Where to find origin node or target node inside obj_b (second argument)
    
    
    """

    nodes = []
    o_flag, t_flag = _get_origin_and_target_implicit_flags(implicit)

    _collect_origin_node_pairs( nodes, obj_a, obj_b, implicit=o_flag )
    _collect_target_node_pairs( nodes, obj_a, obj_b, implicit=t_flag )
    return nodes 



class QtBase:
    # some base function for all Qt Pydev,gr objects 
    _connection = None

    @classmethod
    def get_widget_class(cls):
        raise NotImplementedError("get_widget_class") 
    
    @property
    def widget(self):
        return self.engine.widget     
    
    def resolve_origin(self, parent, implicit=False):
        opath = self.config.origin 
        if isinstance( opath, BaseObject):
            return opath 
        if opath is None:
            if implicit:
                return getattr( parent, self.name)
            else:
                return None 
        else:
            if parent is None:
                raise ValueError("Cannot resolve origin path without parent")
            return objpath(opath).resolve(parent)
    
    
    def resolve_target(self, parent, implicit=False):
        opath = self.config.target 
        if isinstance( opath, BaseObject):
            return opath 
        if opath is None:
            if implicit:
                return getattr( parent, self.name)
            else:
                return None 
        else:
            if parent is None:
                raise ValueError("Cannot resolve target path without parent")
            return objpath(opath).resolve(parent)

    def kill(self):
        self.clear()
        if self._connection:
            self._connection.disconnect() 

    def clear(self):
        for obj in self.find(QtBase):
            obj.clear()
        self.engine.clear()
    
    def get_connection_pairs(self, 
            obj: Optional[BaseObject] =None, 
            implicit: Implicit=Implicit.none
        ) -> Tuple[BaseNode, BaseNode]:
        nodes = []
        o_flag, t_flag = _get_origin_and_target_implicit_flags(implicit)

        _collect_origin_node_pairs( nodes, self, obj, implicit=o_flag )
        _collect_target_node_pairs( nodes, self, obj, implicit=t_flag )
        return nodes 
