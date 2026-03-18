from __future__ import annotations

from datetime import UTC, datetime

from app.audit.utility import hash_event

class HashChainedAuditMixin:

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.events = [] or self.events

    def verify_chain(self) -> bool:
        prev_hash = "genesis"
        invalid_index = None
        index = 0 

        for event in self.events:
            if prev_hash and event["prev_hash"] != prev_hash:
                return False, index
            expected_hash = hash_event(event["event"], prev_hash)
            if event["hash_self"] != expected_hash:
                print(f"Hash mismatch for event {event['id']}: expected hash {expected_hash}, got {event['hash_self']}")
                return False
            prev_hash = event["hash_self"]
            index += 1
        return True

    def verify_chain_in_file(self) -> bool:
        with open(Config.AUDIT_FILE, "r", encoding="utf-8") as f:
            hash_prev = None
            invalid_index = None
            index = 0 
            for line in f: 
                if len(line.strip()) == 0: continue 
                try: 
                    event = json.loads(line) 

                    if hash_prev and event["hash_prev"] != hash_prev:
                        return False, index

                    hash_prev = event["hash_self"] 
                    index += 1 

                    expected_hash = hash_event(event["event"], hash_prev)
                    if event["hash_self"] != expected_hash:
                        print(f"Hash mismatch for event {event['id']}: expected {expected_hash}, got {event['hash_self']}")
                        return False
                    hash_prev = event["hash_self"]
                except:
                    print(f"could not load line: {line}")
                    pass
        return True, None 