from __future__ import annotations
from enum import Enum
import json

from app.mixins.json_serializable import JsonSerializableMixin
from app.rules.rule_status import RuleStatus


class RuleResult(JsonSerializableMixin):
    def __init__(self, status: RuleStatus, code: str):
        self.status = status 
        self.code = code  

    def __repr__(self):
        return f"RuleResult(status={self.status}, code={self.code})"