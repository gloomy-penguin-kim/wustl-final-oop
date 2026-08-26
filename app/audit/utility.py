import json 
import hashlib
from datetime import datetime, UTC
from typing import Any


@staticmethod
def normalize_date(date: Any = None) -> str:
    if not date:
        date = datetime.now(UTC)
    if isinstance(date, datetime):
        date = date.isoformat()
    return date


@staticmethod
def hash_event(payload: dict) -> str:
    canonical = json.dumps(payload, sort_keys=True, ensure_ascii=True, indent=None)
    return hashlib.sha256(canonical.encode()).hexdigest()
