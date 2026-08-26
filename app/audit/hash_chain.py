from __future__ import annotations

import json
import logging
from datetime import datetime, UTC

from typing import Tuple

from app.audit.event_sink import emit
from app.audit.utility import hash_event, normalize_date
from app.settings import Config
from app.mixins.hash_chain_mixin import HashChainAuditMixin 
  

class HashChain(HashChainAuditMixin):

    def __init__(self, filename: str = None, **kwargs):
        super().__init__(**kwargs)
        self.chain = []
        self.filename = filename or Config.AUDIT_FILE
        self.last_hash = self._get_last_hash_from_file() or "genesis"

    def append(self, event: dict):
        event["hash_prev"] = self.last_hash or self._get_last_hash_from_file() or "genesis"
        event["date"] = normalize_date(event.get("date", None))
        hash_self = hash_event(event)
        event["hash_self"] = hash_self 
        self.last_hash = hash_self
        self.chain.append(event)
        with open(self.filename, "a") as f:
            f.write(json.dumps(event, default=str, ensure_ascii=True, indent=None) + "\n")
        emit.emit(event={
            "event": event.get("event"),
            "date": datetime.now(UTC),
            "data": event.get("data"),
            "id": event.get("id")
        })

    def clear(self):
        with open(self.filename, "w", encoding="utf-8") as f:
            f.write("")
        self.chain = []
        self.last_hash = "genesis"
        emit.emit(event={
            "event": "Clearing hash chain file",
            "id": self.filename,
            "date": datetime.now(UTC),
        })

    def _get_last_hash_from_file(self):
        count = 0 
        last_hash = None
        try:   
            with open(self.filename, "r", encoding="utf-8") as f:
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
            logging.warning(f"Audit file has {count} records, which may impact performance: {self.filename}")
        return last_hash

    def __len__(self) -> int:
        return len(self.chain)

    def verify_chain(self):
        return self.verify_chain_in_file()

hc = HashChain()