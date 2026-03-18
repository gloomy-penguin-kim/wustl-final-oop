from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import UTC, datetime
import json
from typing import Tuple

from app.audit.event_sink import EmitEvent
from app.domain.decision import Decision
from app.rules.rule_base import Rule
from app.rules.rule_registry import RULE_REGISTRY

class Policy(EmitEvent, ABC):

    def __init__(self, *, version: str, type: str, rules: list[Rule] | None = None): 
        self._version = version 
        self._type = type 
        self._rules = rules or [] 
        self._created_at = datetime.now(UTC)   
  
    @classmethod
    def is_list_of_strings(cls, obj):
        return isinstance(obj, list) and all(isinstance(elem, str) for elem in obj)
          
    @property
    def version(self) -> str:
        return self._version
    
    @property
    def type(self) -> str:
        return self._type
    
    @property
    def rules(self) -> list[Rule]:
        return self._rules
    
    @property
    def created_at(self) -> datetime:
        return self._created_at

    @abstractmethod
    def evaluate(self, app) -> Tuple[Decision, dict]:
        pass

    def to_dict(self):  
        data = {} 
        data["version"] = self.version
        data["rules"] = [r.__class__.__name__ for r in self.rules]
        data["type"] = self.type
        data["created_at"] = self.created_at if isinstance(self.created_at, str) else self.created_at.isoformat() 
        return data 

    def to_json(self):   
        return json.dumps(self.to_dict(), sort_keys=True) 