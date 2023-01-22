
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, Hashable, List, Optional, Tuple, Union

from pydevmgr_core import Downloader, Uploader
from pydevmgr_core.base.datamodel import DataLink
from pydevmgr_core.base.download import DownloaderConnection
from pydevmgr_core.base.node import BaseNode
from pydevmgr_core.base.upload import UploaderConnection

     

def node_transfert(nodes, down_data, up_data):
    for down, up in nodes:
        up_data[up] = down_data[down]

          

@dataclass 
class Connector:
    downloader: Union[Downloader, DownloaderConnection] = field( default_factory=Downloader)
    uploader: Union[Uploader, UploaderConnection] = field( default_factory=Uploader)
    
    def __post_init__(self):
        self.downloader_connection = self.downloader.new_connection()
        self.uploader_connection = self.uploader.new_connection()
        self._token = ( (self.downloader_connection._token), (self.uploader_connection._token) )


        downloader = self.downloader_connection._downloader
        uploader = self.uploader_connection._uploader
        self.downloader_connection.add_callback( uploader.upload ) 
        
        self.update = downloader.download 
        

    def add_datalinks(self, datalinks= List[ Tuple[DataLink, DataLink]  ]): 
        for left, right in datalinks:
            if left:  self.downloader_connection.add_datalink(left)
            if right: self.uploader_connection.add_datalink(right)
    
    def add_nodes(self, nodes = List[ Tuple[BaseNode, BaseNode]]):
        
            down_nodes, _ = zip(*nodes) 
            self.downloader_connection.add_nodes( down_nodes)
           
            def node_transfert_callback():
                data = self.downloader_connection._downloader.data 
                upload_data = self.uploader_connection._uploader.node_values
                node_transfert(nodes, data, upload_data)

            def node_transfert_ones():
                # This callback should be called ones per connection 
                # I do this to avoid to have None values before a first download 
                data = self.downloader_connection._downloader.data 
                upload_data = {} 
                node_transfert(nodes, data, upload_data)
                # add the nodes and remove myself from callback 
                self.uploader_connection.add_nodes( upload_data )
                self.downloader_connection.remove_callback( node_transfert_ones )
                self.downloader_connection.add_callback( node_transfert_callback) 
            
            self.downloader_connection.add_callback( node_transfert_ones ) 
    
    def new_connection(self):
        return Connector( self.downloader_connection, self.uploader_connection)

    def add_callbacks(self, callbacks):
        for callback in callbacks:
            self.uploader_connection.add_callback( callback) 
        
    def disconnect(self):
        self.downloader_connection.disconnect()
        self.uploader_connection.disconnect()
    

    def update(self):
        raise NotImplementedError("Connector has not been ignitialized correctly")

 
