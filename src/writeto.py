
from abc import ABC
import io

from settings import Config
from models import Event


class EventWriteTo(ABC): 
    def write(self, event: Event) -> None:...
class EventWriteToFile(EventWriteTo):
    def write(self, event: Event) -> None:
        with open(Config.AUDIT_FILE, "a") as f: 
            f.write(event.to_json() +"\n")
class EventWriteToStringIO(EventWriteTo):
    def write(self, event: Event) -> None:
        buffer = io.StringIO()
        buffer.write(event.to_json() +"\n") 
        buffer.close() 
class EventWriteToPrint(EventWriteTo):
    def write(self, event: Event) -> None:
        print("Emitting Event:", event.loan_id, event.event) 