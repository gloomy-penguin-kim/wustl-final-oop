from __future__ import annotations

from datetime import UTC, datetime
from typing import Tuple
import json 

from app.settings import Config 
from app.audit.utility import hash_event

class HashChainAuditMixin:

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.events = [] 

    def verify_chain_in_memory(self) -> Tuple[bool, int | None]:
        prev_hash = "genesis"
        invalid_index = None
        index = 0 
        for event in self.events:
            if prev_hash and event["prev_hash"] != prev_hash:
                return (False, index)
            expected_hash = hash_event(event["event"], prev_hash)
            if event["hash_self"] != expected_hash:
                print(f"Hash mismatch for event {event['id']}: expected hash {expected_hash}, got {event['hash_self']}")
                return (False, index)
            prev_hash = event["hash_self"]
            index += 1
        return (True, None) 
 
    @classmethod
    def verify_chain_in_file(cls) -> Tuple[bool, int | None]:
        with open(Config.AUDIT_FILE, "r", encoding="utf-8") as f:
            hash_prev = None
            invalid_index = None
            index = 0 
            for line in f: 
                if len(line.strip()) == 0: continue 
                # try: 
                event = json.loads(line) 

                if hash_prev and event["hash_self"] != hash_prev:
                    print(f"Hash mismatch for event {event['id']}: expected previous hash {hash_prev}, got {event['hash_self']}")
                    return False, index

                hash_prev = event["hash_self"] 
                index += 1 

                expected_hash = hash_event(event["event"], hash_prev)
                if event["hash_self"] != expected_hash:
                    print(f"Hash mismatch for event {event['id']}: expected {expected_hash}, got {event['hash_self']}")
                    return False
                hash_prev = event["hash_self"]
                # except Exception as e: 
                #     print(f"{e}, could not load line: {line}")
                #     pass
        return True, None 