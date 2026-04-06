from __future__ import annotations

from abc import ABC

import json
  
from app.settings import Config 


class EventSink(ABC):
    def __init__(self, *args, **kwargs):
        pass

    @classmethod
    def emit(cls, event: dict): ...

    @classmethod
    def clear(cls): ...


class FileEventSink(EventSink):
    filename = Config.EVENTS_FILE
    def __init__(self, filename: str = None, *args, **kwargs):
        super().__init__(*args, **kwargs) 
        if filename:
            FileEventSink.filename = filename

    @classmethod
    def emit(cls, event: dict):
        with open(cls.filename, "a") as f:
            f.write(json.dumps(event, default=str) + "\n")
        super().emit(event)

    @classmethod
    def clear(cls):
        with open(cls.filename, "w") as f:
            f.write("")
        super().clear()
 
        
class PrintEventSink(EventSink): 
    def __init__(self, *args, **kwargs): 
        super().__init__(*args, **kwargs) 

    @classmethod
    def emit(cls, event: dict):
        print("emit...",
              event.get("date").strftime("%Y-%m-%d %H:%M"),
              event.get("id"),
              event.get("event"),
              event.get("data") or "")
        super().emit(event)

    @classmethod
    def clear(cls):
        super().clear()


class InMemoryEventSink(EventSink):   
    events = []

    def __init__(self, *args, **kwargs):  
        super().__init__(*args, **kwargs) 

    @classmethod
    def emit(cls, event: dict):
        InMemoryEventSink.events.append(event)
        super().emit(event)

    @classmethod
    def clear(cls):
        InMemoryEventSink.events = []
        super().clear()


class EmitEvent(InMemoryEventSink, FileEventSink, PrintEventSink, EventSink):

    def __init__(self, filename: str = None, *args, **kwargs):
        super().__init__(*args, filename=filename, **kwargs)

    @classmethod
    def emit(cls, event: dict):
        super().emit(event) 

    @classmethod
    def clear(cls):
        super().clear()