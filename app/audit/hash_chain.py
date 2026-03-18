from __future__ import annotations

import hashlib
import json


class HashChain: 

    def __init__(self):
        self.last_hash = {}
        self.events = []
  
    def append(self, event: dict): 
        prev_hash = self.events[-1]["hash_self"] if len(self.events) > 0 else "genisis"
        id = event["id"]
        hash_self = hash_event(event, prev_hash) 
        e = { 
            "id": id, 
            "event": event, 
            "hash_self": hash_self,
            "prev_hash": prev_hash 
        }
        self.events.append(e)
        self.last_hash = hash_self 
        
def hash_event(event: dict, prev_hash: str): 
    payload = json.dumps(event, sort_keys=True) 
    return hashlib.sha256((payload + prev_hash).encode()).hexdigest()