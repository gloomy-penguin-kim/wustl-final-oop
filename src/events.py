
from abc import ABC, abstractmethod
from collections import defaultdict
from datetime import datetime
import uuid

from models import Event
from fileio.events_fileio import EventFileIO
from hash_chained_audit import HashChainedAuditMixin


class EventSink(ABC): 
    def __init__(self):  
        pass 

    @abstractmethod 
    def emit(self, event: dict) -> None:...     
 
    
class EventLogger(EventSink, EventFileIO, HashChainedAuditMixin):
    events = defaultdict(list) 
    def __init__(self, **kwargs): 
        super().__init__(**kwargs) 
        EventLogger.events = EventLogger.events | self.load_file() 
 
    def emit(self, event: dict) -> None: 
        if "event" not in event: 
            raise KeyError(f"Event is missing valid 'event' string.")  
        e = Event().from_dict(event) 
        EventLogger.events[e.loan_id].append(e) 
        self.audit(EventLogger.events[e.loan_id])
        self.write(e)
    
    def get_hash_prev(self, loan_id: uuid.UUID | None):
        if not loan_id: return 
        if loan_id in EventLogger.events and len(EventLogger.events[loan_id]) > 0: 
            return EventLogger.events[loan_id][-1].hash_self 
    
    def hash(self, d: dict) -> int:
        return hash(d["event"] + str(d["loan_id"]) + str(d["timestamp"])) 
        
    def new(self, event: str, loan_id: uuid.UUID | None, timestamp: datetime = datetime.now()):
        d = {
            "event": event, 
            "loan_id": loan_id, 
            "hash_prev": self.get_hash_prev(loan_id), 
            "timestamp": timestamp 
        }
        d["hash_self"] = self.hash(d) 
        self.emit(d) 
    
    def clean(self, loans: list[uuid.UUID]):
        e = defaultdict(list) 
        for loan_id,event in EventLogger.events.items(): 
            if loan_id in loans: 
                e[loan_id] = EventLogger.events[loan_id][:]
        EventLogger.events = e 
        self.save_file(EventLogger.events)

