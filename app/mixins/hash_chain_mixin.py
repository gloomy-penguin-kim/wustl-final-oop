from __future__ import annotations
 
from typing import Tuple 

class HashChainAuditMixin:

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    # def verify_chain_in_memory(self) -> Tuple[bool, int | None]:

    #     prev_hash = "genesis"

    #     for index, event in enumerate(self.chain.items):

    #         # 1. Check linkage
    #         if index > 0 and event.get("hash_prev") != prev_hash:
    #             return False, index

    #         # 2. Recompute expected hash
    #         # clean = self.clean_event(event)
    #         # expected_hash = hash_event(clean, event.get("hash_prev", ""))
    #         #
    #         # if event.get("hash_self") != expected_hash:
    #         #     print(f"Hash mismatch at index {index}: expected {expected_hash}, got {event.get('hash_self')}")
    #         #     return (False, index)

    #         # move forward
    #         prev_hash = event.get("hash_self")

    #     return True, None

    @staticmethod
    def _clean_event(cls, event: dict):
        return {
            k: event[k]
            for k in sorted(event)
            if k not in ("hash_self")
        }


    def verify_chain_in_file(self) -> Tuple[bool, int | None]:
        with open(self.filename, "r", encoding="utf-8") as f:
            hash_prev = None 
            index = 0 
            for line in f: 
                if len(line.strip()) == 0:
                    continue
                # event = json.loads(line)  
                # clean = self._clean_event(event)
                if index > 0 and event.get("hash_prev", None) != hash_prev:
                    return False, index
                hash_prev = event.get("hash_self", None)
                index += 1
        return True, None

