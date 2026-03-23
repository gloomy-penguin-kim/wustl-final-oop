from __future__ import annotations

from abc import ABC, abstractmethod

import json
import logging 
 
from app.audit.hash_chain import HashChain
from .utility import get_last_hash_from_file
from app.settings import Config
from app.mixins.hash_chain_mixin import HashChainAuditMixin

class EventSink(ABC):
    def __init__(self, *args, **kwargs):
        pass

    @abstractmethod
    def emit(self, event: dict):...

    @abstractmethod
    def clear(self):... 


class FileEventSink(EventSink):  
    def __init__(self, filename: str, *args, **kwargs): 
        super().__init__(*args, **kwargs) 
        self.filename = filename 

    def emit(self, event: dict):  
        with open(self.filename, "a") as f:
            f.write(json.dumps(event, default=str) + "\n")     
            
    def clear(self): 
        with open(self.filename, "w") as f: 
            f.write("") 
 
        
class PrintEventSink(EventSink): 
    def __init__(self, *args, **kwargs): 
        super().__init__(*args, **kwargs) 

    def emit(self, event: dict): 
        print("emit...", event["event"], event["id"])  
    
    def clear(self):
        pass


class InMemoryEventSink(EventSink):   
    events = [] 
    def __init__(self, *args, **kwargs):  
        super().__init__(*args, **kwargs) 
         
    def emit(self, event: dict): 
        InMemoryEventSink.events.append(event)  

    def clear(self):  
        InMemoryEventSink.events = [] 


class EmitEvent(InMemoryEventSink, FileEventSink, PrintEventSink):

    def __init__(self, filename: str | None = None, *args, **kwargs): 
        super().__init__(*args, **kwargs) 
        self.filename = filename or Config.EVENTS_FILE

    def emit(self, event: dict): 
        super().emit(event) 

    def clear(self): 
        super().clear() 