from __future__ import annotations

import json
from typing import Tuple

from app.audit.utility import hash_event


class HashChainAuditMixin:

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


    @classmethod
    def _clean_event(cls, event: dict):
        return {
            k: event[k]
            for k in sorted(event)
            if k not in ("hash_self")
        }

    @classmethod
    def verify_chain_in_file(cls) -> Tuple[bool, int | None]:
        with open(cls.filename, "r", encoding="utf-8") as f:
            hash_prev = None 
            index = 0 
            for line in f: 
                if not line: continue
                event = json.loads(line)
                if index > 0 and event.get("hash_prev", None) != hash_prev:
                    return False, index

                clean = cls._clean_event(event)
                hashed = hash_event(clean)
                if hashed != event.get("hash_self"):
                    return False, index

                hash_prev = event.get("hash_self", None)
                index += 1
        return True, None

