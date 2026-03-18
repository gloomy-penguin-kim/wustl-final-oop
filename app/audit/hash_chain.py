from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
import logging 

from app.settings import Config 
from app.mixins.hash_chain_mixin import HashChainedAuditMixin

from .utility import hash_event

class HashChain(HashChainedAuditMixin): 

    def __init__(self):
        self.last_hash = {}
        self.events = []
        
    def _get_last_hash_from_file(self):
        try: 
            with open(Config.AUDIT_FILE, "r", encoding="utf-8") as f: 
                for line in f: 
                    if len(line.strip()) == 0: continue 
                    try: 
                        event = json.loads(line) 
                        self.last_hash = event["hash_self"] 
                    except:
                        logger.warning(f"could not load line: {line}")
                        pass
        except FileNotFoundError:
            logger.warning("Audit file not found, starting new hash chain.")
            pass
  
    def append(self, event: dict): 
        prev_hash = self.events[-1]["hash_self"] if len(self.events) > 0 else "genisis"
        assert prev_hash is not None 
        id = event["id"]
        hash_self = hash_event(event, prev_hash) 
        e = { 
            "id": id, 
            "event": event, 
            "hash_self": hash_self,
            "prev_hash": prev_hash,
            "timestamp": datetime.now(UTC)
        }
        self.events.append(e)
        self.last_hash = hash_self 
            