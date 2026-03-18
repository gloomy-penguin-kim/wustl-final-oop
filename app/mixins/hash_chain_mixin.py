from __future__ import annotations

from datetime import UTC, datetime
from typing import Tuple
import json 

from app.settings import Config 
from app.audit.utility import hash_event

class HashChainAuditMixin:

    def __init__(self, **kwargs):
        super().__init__(**kwargs) 

    def verify_chain_in_memory(self) -> Tuple[bool, int | None]:
        prev_hash = "genesis"

        for index, event in enumerate(self.events):

            # 1. Check linkage
            if index > 0 and event.get("hash_prev") != prev_hash:
                print(f"Linkage error at index {index}: expected previous hash {prev_hash}, got {event.get('hash_prev')}")
                return (False, index)

            # 2. Recompute expected hash
            # clean = self.clean_event(event) 
            # expected_hash = hash_event(clean, event.get("hash_prev", ""))

            # if event.get("hash_self") != expected_hash:
            #     print(f"Hash mismatch at index {index}: expected {expected_hash}, got {event.get('hash_self')}")
            #     return (False, index)

            # move forward
            prev_hash = event.get("hash_self")

        return (True, None)

    def clean_event(self,event: dict):
        return {
            k: event[k]
            for k in sorted(event)
            if k not in ("hash_self", "hash_prev")
        }

    @classmethod
    def verify_chain_in_file(cls) -> Tuple[bool, int | None]:
        with open(Config.AUDIT_FILE, "r", encoding="utf-8") as f:
            hash_prev = None
            invalid_index = None
            index = 0 
            for line in f: 
                if len(line.strip()) == 0: continue  
                event = json.loads(line)  
                if index > 0 and event.get("hash_prev", None) != prev_hash:
                    return (False, index) 

                prev_hash = event.get("hash_self", None)
                index += 1
        return (True, None) 

    @classmethod 
    def clear_file(cls): 
        with open(Config.AUDIT_FILE, "w", encoding="utf-8") as f:
            f.write("")