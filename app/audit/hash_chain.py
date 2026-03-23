from __future__ import annotations
 
import hashlib  
import json
import logging 

from datetime import UTC, datetime
from typing import Tuple

from app.settings import Config 
from app.mixins.hash_chain_mixin import HashChainAuditMixin 
 
 

class HashChain(HashChainAuditMixin): 
    items = [] 
    def __init__(self, filename: str | None = None, **kwargs): 
        super().__init__(**kwargs)  
        self.filename = filename or Config.AUDIT_FILE 
        self.last_hash = self._get_last_hash_from_file() or "genesis" 
        self.events = [] 
  
    def append(self, event: dict):  
        event["hash_prev"] = self.last_hash
        event["timestamp"] = self.normalize_timestamp(event["timestamp"])  
        hash_self = self.hash_event(event)  
        event["hash_self"] = hash_self 
        self.last_hash = hash_self   
        HashChain.items.append(event)   
        with open(self.filename, "a") as f:
            f.write(json.dumps(event, default=str) + "\n")  
        return event 
    
    def normalize_timestamp(self, timestamp) -> str: 
        if not timestamp: 
            timestamp = datetime.now(UTC)
        if isinstance(timestamp, datetime): 
            timestamp = timestamp.isoformat() 
        return timestamp 
    
    def hash_event(self, payload: dict) -> str: 
        canonical = json.dumps(payload, sort_keys=True, ensure_ascii=False, indent=None)
        return hashlib.sha256(canonical.encode()).hexdigest()
     
    def verify_chain(self) -> Tuple[bool, int | None]:
        return self.verify_chain_in_memory() 

    def clear(self):   
        with open(self.filename, "w", encoding="utf-8") as f:
            f.write("")
        HashChain.items = [] 
        self.last_hash = "genesis"
    
    def _get_last_hash_from_file(self):
        count = 0 
        last_hash = None
        try:   
            with open(self.filename, "r", encoding="utf-8") as f:
                for line in f: 
                    if len(line.strip()) == 0: continue 
                    count += 1 
                    try: 
                        event = json.loads(line)
                        if event["type"] == "emit" and "hash_self" in event: 
                            last_hash = event["hash_self"] 
                            count += 1 
                    except:
                        logging.warning(f"could not load line: {line}")
                        pass
        except FileNotFoundError:
            logging.warning("Audit file not found, starting new hash chain.")
            pass
        if count > 1000: 
            logging.warning(f"Audit file has {count} records, which may impact performance: {self.filename}")
        return last_hash

