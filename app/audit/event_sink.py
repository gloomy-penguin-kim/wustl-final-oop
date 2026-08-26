from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime, UTC

import json
  
from app.settings import Config 


class EventSink(ABC):
    def __init__(self, *args, **kwargs):
        pass

    @abstractmethod
    def emit(self, event: dict): ...

    @abstractmethod
    def clear(self): ...


class FileEventSink(EventSink):

    def __init__(self, filename: str = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.filename = filename or Config.EVENTS_FILE

    def emit(self, event: dict):
        with open(self.filename, "a") as f:
            f.write(json.dumps(event, default=str) + "\n")
        super().emit(event)

    def clear(self):
        with open(self.filename, "w") as f:
            f.write("")
        super().clear()

        
class PrintEventSink(EventSink): 
    def __init__(self, *args, **kwargs): 
        super().__init__(*args, **kwargs) 

    def emit(self, event: dict):
        print("emit...",
              event.get("date").strftime("%Y-%m-%d %H:%M"),
              event.get("id"),
              event.get("event"),
              event.get("data") or "")
        super().emit(event)

    def clear(self):
        super().clear()


class InMemoryEventSink(EventSink):
    def __init__(self, *args, **kwargs):  
        super().__init__(*args, **kwargs)
        self.events = []

    def emit(self, event: dict):
        self.events.append(event)
        super().emit(event)

    def clear(self):
        self.events = []
        super().clear()


class EmitEvent(InMemoryEventSink, FileEventSink, PrintEventSink, EventSink):

    def __init__(self, filename: str = None, *args, **kwargs):
        super().__init__(*args, filename=filename, **kwargs)

    def emit(self, event: dict):
        super().emit(event) 

    def clear(self):
        super().clear()

emit = EmitEvent()