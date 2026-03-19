from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import UTC, datetime
from typing import Tuple, cast

from app.audit.event_sink import EmitEvent
from app.domain import LoanApplication
from app.domain.decision import Decision
from app.mixins.json_serializable import JsonSerializableMixin
from app.policies.policy_registry import POLICY_REGISTRY
from app.rules import Rule
from app.rules import RULE_REGISTRY

class Policy(JsonSerializableMixin, EmitEvent, ABC):

    def __init__(self,
                 version: str,
                 type: str,
                 rules: list[Rule] | None = None,
                 created_at: datetime = None,):
        self._version = version 
        self._type = type 
        self._rules = rules or [] 
        self._created_at = created_at or datetime.now(UTC)

    @abstractmethod
    def evaluate(self, app: LoanApplication) -> Tuple[Decision, dict]:...

    def policy_selected(self, app: LoanApplication):
        self.emit({
            "event": "POLICY_SELECTED",
            "id": app.application_id + "_" + self.version + "_" + datetime.now(UTC).isoformat(),
            "application_id": app.application_id,
            "policy_version": self.version
        })

    def policy_evaluated(self, app: LoanApplication):
        self.emit({
            "event": "POLICY_EVALUATED",
            "id": app.application_id + "_" + self.version + "_" + datetime.now(UTC).isoformat(),
            "application_id": app.application_id,
            "policy_version": self.version
        })

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
        return cast(list[Rule], (rules or []))

    @classmethod
    def is_list_of_strings(cls, obj):
        return isinstance(obj, list) and all(isinstance(elem, str) for elem in obj)

    def to_dict(self):  
        data = dict()
        data["version"] = self.version
        data["rules"] = self.rules_as_strings
        data["type"] = self.type
        data["created_at"] = self.created_at #if isinstance(self.created_at, str) else self.created_at.isoformat()
        return data

    @classmethod
    def from_dict(cls, data: dict) -> Policy:
        created_at = data.get("created_at", datetime.now(UTC))
        created_at = created_at if isinstance(created_at, datetime) else datetime.fromisoformat(created_at)
        return POLICY_REGISTRY[data.get("type")](data.get("version"),
                                                 data.get("rules"),
                                                 created_at)
