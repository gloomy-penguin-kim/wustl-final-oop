from __future__ import annotations

from abc import ABC, abstractmethod

import json
import logging 
 
from app.audit.hash_chain import HashChain
from .utility import get_last_hash_from_file
from app.settings import Config
from app.mixins.hash_chain_mixin import HashChainAuditMixin

class EventSink(ABC):
    def __init__(self, **kwargs):
        pass

    @abstractmethod
    def emit(self, event: dict):...

    @abstractmethod
    def clear(self):... 


class FileEventSink(HashChainAuditMixin, EventSink):  
    def __init__(self, **kwargs): 
        super().__init__( **kwargs) 

    def emit(self, event: dict): 
        if "type" not in event: 
            event["type"] = "emit" 
        with open(Config.AUDIT_FILE, "a") as f:
            f.write(json.dumps(event, default=str) + "\n")    
        super().emit(event)  
            
    def clear(self): 
        with open(Config.AUDIT_FILE, "w") as f: 
            f.write("")
        super().clear()
 
        
class PrintEventSink(EventSink): 
    def __init__(self, **kwargs): 
        super().__init__(**kwargs) 

    def emit(self, event: dict): 
        print("emit...", event["event"], event["id"]) 
        super().emit(event)  
    
    def clear(self):
        super().clear() 


class AuditEventSink(EventSink): 
    chain = HashChain()
    def __init__(self, **kwargs): 
        super().__init__(**kwargs) 
         
    def emit(self, event: dict): 
        event = AuditEventSink.chain.append(event) 
        super().emit(event) 

    def clear(self): 
        AuditEventSink.chain = HashChain() 
        super().clear()


class EmitEvent(AuditEventSink, FileEventSink, PrintEventSink):

    def __init__(self, **kwargs): 
        super().__init__(**kwargs) 

    def emit(self, event: dict): 
        super().emit(event) 

    def clear(self): 
        super().clear() 