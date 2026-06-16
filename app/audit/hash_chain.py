from __future__ import annotations

import json
import logging
from datetime import datetime, UTC

from typing import Tuple

from app.audit import EmitEvent
from app.audit.utility import hash_event, normalize_date
from app.settings import Config
from app.mixins.hash_chain_mixin import HashChainAuditMixin 
  

class HashChain(HashChainAuditMixin):
    last_hash = None
    chain = []
    filename = Config.AUDIT_FILE

    def __init__(self, filename: str = None, **kwargs):
        super().__init__(**kwargs)
        HashChain.filename = filename or HashChain.filename
        HashChain.last_hash = self._get_last_hash_from_file() or "genesis"

    @classmethod
    def append(cls, event: dict):
        event["hash_prev"] = HashChain.last_hash or cls._get_last_hash_from_file() or "genesis"
        event["date"] = normalize_date(event.get("date", None))
        hash_self = hash_event(event)
        event["hash_self"] = hash_self 
        cls.last_hash = hash_self
        cls.chain.append(event)
        with open(cls.filename, "a") as f:
            f.write(json.dumps(event, default=str, ensure_ascii=True, indent=None) + "\n")

        EmitEvent.emit(event={
            "event": event.get("event"),
            "date": datetime.now(UTC),
            "data": event.get("data"),
            "id": event.get("id")
        })

    @classmethod
    def verify_chain(cls) -> Tuple[bool, int | None]:
        return cls.verify_chain_in_file()

    @classmethod
    def clear(cls):
        with open(cls.filename, "w", encoding="utf-8") as f:
            f.write("")
        cls.chain = []
        cls.last_hash = "genesis"
        EmitEvent.emit(event={
            "event": "Clearing hash chain file",
            "id": cls.filename,
            "date": datetime.now(UTC),
        })

    @classmethod
    def _get_last_hash_from_file(cls):
        count = 0 
        last_hash = None
        try:   
            with open(HashChain.filename, "r", encoding="utf-8") as f:
                for line in f: 
                    if not line: continue
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

    def __len__(self) -> int:
        return len(self.chain)