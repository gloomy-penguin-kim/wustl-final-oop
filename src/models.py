from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime
import uuid

from serializable import SerializableMixin
  

@dataclass(frozen=True, slots=True)
class Event(SerializableMixin): 
    event: str | None = None 
    loan_id: uuid.UUID | None = None  
    hash_self: int | None = None 
    hash_prev: int | None = None 
    timestamp: datetime = datetime.now() 

    def from_dict(self, d: dict):
        return Event(event=d["event"], 
                    loan_id=d["loan_id"], 
                    hash_self=d["hash_self"], 
                    hash_prev=d["hash_prev"],
                    timestamp=d["timestamp"])