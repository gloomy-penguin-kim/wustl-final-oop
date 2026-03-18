from __future__ import annotations

from abc import ABC, abstractmethod

import json

from app.audit.hash_chain import HashChain
from app.settings import Config

class EventSink(ABC):

    @abstractmethod
    def emit(self, event: dict):...

    @abstractmethod
    def clear(self):... 


class FileEventSink(EventSink): 
    filename = Config.AUDIT_FILE
    def __init__(self, **kwargs): 
        super().__init__(**kwargs) 

    def emit(self, event: dict):
        super().emit(event) 
        if "type" not in event: 
            event["type"] = "emit" 
        with open(FileEventSink.filename, "a") as f:
            f.write(json.dumps(event, default=str) + "\n")    
    
    def clear(self): 
        with open(FileEventSink.filename, "w") as f: 
            f.write("")
 
        
class PrintEventSink(EventSink): 
    def __init__(self, **kwargs): 
        super().__init__(**kwargs) 

    def emit(self, event: dict): 
        super().emit(event)  
        print("emit...", event["event"], event["id"]) 
    
    def clear(self):
        pass

class AuditEventSink(EventSink): 
    chain = HashChain()
    def __init__(self, **kwargs):
        super().__init__(**kwargs) 
         
    def emit(self, event: dict):
        super().emit(event) 
        AuditEventSink.chain.append(event) 
    
    def clear(self): 
        AuditEventSink.chain = HashChain() 


class EmitEvent(FileEventSink, PrintEventSink, AuditEventSink):

    def __init__(self, **kwargs): 
        super().__init__(**kwargs) 

    def emit(self, event: dict):
        super().emit(event) 

    def clear(self): 
        super().clear() 