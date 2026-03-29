from __future__ import annotations

from abc import ABC, abstractmethod

import json
import logging 
  
from app.settings import Config 


class EventSink(ABC):
    def __init__(self, *args, **kwargs):
        pass

    @abstractmethod
    def emit(self, event: dict): ...

    @abstractmethod
    def clear_sink(self): ...


class FileEventSink(EventSink):  
    def __init__(self, events_filename: str, *args, **kwargs): 
        super().__init__(*args, **kwargs) 
        self.events_filename = events_filename or Config.EVENTS_FILE
        print("self.events_filename", self.events_filename)

    def emit(self, event: dict):  
        with open(self.events_filename, "a") as f:
            f.write(json.dumps(event, default=str) + "\n")     
            
    def clear_sink(self): 
        with open(self.events_filename, "w") as f: 
            f.write("") 
 
        
class PrintEventSink(EventSink): 
    def __init__(self, *args, **kwargs): 
        super().__init__(*args, **kwargs) 

    def emit(self, event: dict): 
        print("emit...", event.get("event"), event.get("id"))
    
    def clear_sink(self):
        pass


class InMemoryEventSink(EventSink):   
    events = []

    def __init__(self, *args, **kwargs):  
        super().__init__(*args, **kwargs) 
         
    def emit(self, event: dict): 
        InMemoryEventSink.events.append(event)   

    def clear_sink(self):  
        InMemoryEventSink.events = [] 


class EmitEvent(InMemoryEventSink, FileEventSink, PrintEventSink):

    def __init__(self, events_filename: str | None = None, *args, **kwargs):  
        super().__init__(*args, events_filename=events_filename, **kwargs)

    def emit(self, event: dict): 
        super().emit(event) 

    def clear_sink(self): 
        super().clear_sink()