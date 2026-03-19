from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import UTC, datetime
import json
from decimal import Decimal
from typing import Tuple, cast

from app.audit.event_sink import EmitEvent
from app.domain.decision import Decision
from app.mixins.json_serializable import JsonSerializableMixin
from app.rules.rule_base import Rule
from app.rules.rule_registry import RULE_REGISTRY

class Policy(JsonSerializableMixin, EmitEvent, ABC):

    def __init__(self, *, version: str, type: str, rules: list[Rule] | None = None): 
        self._version = version 
        self._type = type 
        self._rules = rules or [] 
        self._created_at = datetime.now(UTC)    

    def evaluate(self, app) -> Tuple[Decision, dict]:...


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

    @property
    def rules_as_strings(self) -> list[str]:
        rules = self.rules
        if rules and not Policy.is_list_of_strings(rules):
            rules = [r.__class__.__name__ for r in rules]
        return rules

    @classmethod
    def str_to_rules(cls, rules: list[str] | None) -> list[Rule]:
        if Policy.is_list_of_strings(rules):
            r = []
            for s in (rules or []):
                r.append(RULE_REGISTRY[s]())
            return r
        return cast(list[Rule], rules)

    @classmethod
    def is_list_of_strings(cls, obj):
        return isinstance(obj, list) and all(isinstance(elem, str) for elem in obj)

    def to_dict(self):  
        data = dict()
        data["version"] = self.version
        data["rules"] = self.rules_as_strings
        data["type"] = self.type
        data["created_at"] = self.created_at if isinstance(self.created_at, str) else self.created_at.isoformat() 
        return data