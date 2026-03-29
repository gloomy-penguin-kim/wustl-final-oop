from __future__ import annotations
 
import hashlib  
import json
import logging 

from datetime import UTC, datetime
from typing import Tuple, Any

from app.settings import Config 
from app.mixins.hash_chain_mixin import HashChainAuditMixin 
  

class HashChain(HashChainAuditMixin):
    last_hash = "genesis"
    chain = []
    audit_filename = Config.AUDIT_FILE

    def __init__(self, audit_filename: str | None =  None, **kwargs):
        super().__init__(**kwargs)
        HashChain.last_hash = self._get_last_hash_from_file() or "genesis"
        HashChain.audit_filename = audit_filename or HashChain.audit_filename
        print("HashChain.audit_filename", HashChain.audit_filename)
          
    def chain_event(self, event: dict):  
        event["hash_prev"] = HashChain.last_hash
        event["timestamp"] = self.normalize_timestamp(event.get("timestamp", None))  
        hash_self = self.hash_event(event)  
        event["hash_self"] = hash_self 
        HashChain.last_hash = hash_self
        HashChain.chain.append(event)
        with open(HashChain.audit_filename, "a") as f:
            f.write(json.dumps(event, default=str, sort_keys=True, ensure_ascii=True, indent=None) + "\n")  

    def normalize_timestamp(self, timestamp: Any = None) -> str:
        if not timestamp: 
            timestamp = datetime.now(UTC)
        if isinstance(timestamp, datetime): 
            timestamp = timestamp.isoformat() 
        return timestamp 
    
    def hash_event(self, payload: dict) -> str: 
        canonical = json.dumps(payload, sort_keys=True, ensure_ascii=True, indent=None)
        return hashlib.sha256(canonical.encode()).hexdigest()
     
    def verify_chain(self) -> Tuple[bool, int | None]:
        return self.verify_chain_in_file() 

    def clear(self):   
        with open(HashChain.audit_filename, "w", encoding="utf-8") as f:
            f.write("")
        HashChain.chain = []
        HashChain.last_hash = "genesis"
    
    def _get_last_hash_from_file(self):
        count = 0 
        last_hash = None
        try:   
            with open(self.audit_filename, "r", encoding="utf-8") as f:
                for line in f: 
                    if len(line.strip()) == 0: continue 
                    count += 1 
                    try: 
                        event = json.loads(line)
                        if "hash_self" in event:
                            last_hash = event["hash_self"] 
                            count += 1 
                    except:
                        logging.warning(f"could not load line: {line}")
                        pass
        except FileNotFoundError:
            logging.warning("Audit file not found, starting new hash chain.")
            pass
        if count > 1000: 
            logging.warning(f"Audit file has {count} records, which may impact performance: {self.audit_filename}")
        return last_hash

