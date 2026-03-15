from __future__ import annotations
from enum import Enum
import json

from app.mixins.json_serializable import JsonSerializableMixin

class Status(Enum):
    APPROVE = "APPROVE"
    DECLINE = "DECLINE"
    REFER = "REFER"
 
    def to_dict(self):
        return self.value

    @classmethod
    def from_dict(cls, value):
        return cls(value)

    def to_json(self):
        return json.dumps(self.to_dict())

    @classmethod
    def from_json(cls, s):
        return cls.from_dict(json.loads(s))
    
class RuleResult(JsonSerializableMixin):
    def __init__(self, status: Status, code: str): 
        self.status = status 
        self.code = code  
 