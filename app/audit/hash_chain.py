from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
import logging 
from typing import Tuple

from app.settings import Config 
from app.mixins.hash_chain_mixin import HashChainAuditMixin
from app.persistence import JsonStore
from .utility import get_last_hash_from_file

from .utility import hash_event

class ListNode: 
    def __init__(self, event: dict, hash_prev: str):
        self.event = event
        self.hash_prev = hash_prev
        self.hash_self = hash_event(event, hash_prev)
        self.next = None 

class HashChain(HashChainAuditMixin): 
    items = [] 
    def __init__(self, **kwargs): 
        super().__init__(**kwargs)  
        self.events = [] 
        self.last_hash = get_last_hash_from_file() or "genesis" 
        self.head = None
        self.tail = None

    def clear(self): 
        super().clear() 
        HashChain.items = [] 
        self.last_hash = "genesis"
  
    def append(self, event: dict): 
        prev_hash = self.last_hash 
        assert prev_hash is not None  

        event["timestamp"] = datetime.now(UTC).isoformat() if "timestamp" not in event else event["timestamp"]
        event["timestamp"] = event["timestamp"].isoformat() if isinstance(event["timestamp"], datetime) else event["timestamp"]
        assert isinstance(event["timestamp"], str)

        hash_self = hash_event(event, prev_hash) 

        event["hash_self"] = hash_self
        event["hash_prev"] = prev_hash

        self.events.append(event)   
        self.last_hash = hash_self  
        return event 
    
    def verify_chain(self) -> Tuple[bool, int | None]:
        return self.verify_chain_in_memory()
            