from __future__ import annotations
import hashlib
import json


class HashChain:


    def __init__(self):
        self.last_hash = {}
        self.events = []


    def append(self, event: dict, application_id: str): 
        prev_hash = self.last_hash.get(application_id, "GENESIS") 
        payload = json.dumps(event, sort_keys=True) 
        hash_self = hashlib.sha256((payload + prev_hash).encode()).hexdigest()

        record = {
            "application_id": application_id,
            **event,
            "hash_prev": prev_hash,
            "hash_self": hash_self,
        }

        self.events.append(record) 
        self.last_hash[application_id] = hash_self 
        return record


    def verify(self): 
        prev_hash = "GENESIS" 
        for i, event in enumerate(self.events): 
            payload = json.dumps(
                {k: v for k, v in event.items() if k not in ("hash_prev", "hash_self")},
                sort_keys=True,
            ) 
            expected = hashlib.sha256((payload + prev_hash).encode()).hexdigest() 
            if event["hash_prev"] != prev_hash or event["hash_self"] != expected:
                return False, i 
            prev_hash = event["hash_self"]  
        return True, None
    

def hash_event(event, prev_hash): 
    payload = json.dumps(event, sort_keys=True) 
    return hashlib.sha256((payload + prev_hash).encode()).hexdigest()