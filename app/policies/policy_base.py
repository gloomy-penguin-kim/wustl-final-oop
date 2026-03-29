from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import UTC, datetime
import json
from typing import Any, Tuple, cast

from app.audit.event_sink import EmitEvent
from app.audit.hash_chain import HashChain
from app.domain import LoanApplication
from app.domain.decision import Decision 
from app.mixins.json_serializable import JsonSerializableMixin
from app.policies.policy_registry import POLICY_REGISTRY
from app.rules import Rule
from app.rules import RULE_REGISTRY


class Policy(EmitEvent, JsonSerializableMixin, HashChain, ABC):

    def __init__(self,  
                 version: str,
                 rules: list[Rule] | None = None,
                 created_at: datetime | None = None,
                 **kwargs):
        super().__init__(**kwargs)
        self._version = version 
        self._type = self.__class__.__name__
        self._rules = rules or [] 
        self._created_at = created_at or datetime.now(UTC) 

        self.validate()
         
    @abstractmethod
    def evaluate(self, app: LoanApplication) -> Tuple[Decision, dict]: ...

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
        return cast(list[str], rules) 

    def validate(self): 
        if len(self._version.strip()) == 0: 
            raise ValueError("Policy Version cannot be blank")
        if self._type not in POLICY_REGISTRY:  
            raise ValueError(f"Policy Type is invalid: {self._type}")
        for r in self._rules: 
            if r.__class__.__name__ not in RULE_REGISTRY:
                raise ValueError(f"Policy Rule is invalid: {r.__class__.__name__}")

    def policy_selected(self, app: LoanApplication): 
        self.chain_event({
            "event": "POLICY_SELECTED",
            "id": app.application_id + "_" + self.version + "_" + datetime.now(UTC).isoformat(),
            "application_id": app.application_id,
            "policy_version": self.version
        })

    def policy_evaluated(self, app: LoanApplication): 
        self.chain_event({
            "event": "POLICY_EVALUATED",
            "id": app.application_id + "_" + self.version + "_" + datetime.now(UTC).isoformat(),
            "application_id": app.application_id,
            "policy_version": self.version
        })

    @classmethod
    def str_to_rules(cls, rules: Any) -> list[Rule]:
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
        data["created_at"] = self.created_at
        return data

    @classmethod
    def from_dict(cls, data: dict) -> Policy:
        created_at = data.get("created_at", datetime.now(UTC))
        created_at = created_at if isinstance(created_at, datetime) else datetime.fromisoformat(created_at)
        return POLICY_REGISTRY[data.get("type")](data.get("version"),
                                                 data.get("rules"),
                                                 created_at)

    