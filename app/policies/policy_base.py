from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import UTC, datetime
import json
from typing import Any, Tuple, cast

from app.audit import HashChain, EmitEvent
from app.domain.base_entity import BaseEntity
from app.domain.decision import Decision
from app.domain.domain_registry import register_domain
from app.mixins.validate_policy import ValidatePolicyMixin
from app.policies.policy_registry import POLICY_REGISTRY
from app.rules import Rule
from app.rules import RULE_REGISTRY
from app.audit.event_sink import emit

class Policy(ValidatePolicyMixin, BaseEntity, ABC):
    def __init__(self,
                 rules = None,
                 **kwargs):
        rr = []
        if self.is_list_of_strings(rules):
            r = []
            for s in (rules or []):
                r.append(RULE_REGISTRY[s]())
            rr = r
        else:
            rr = cast(list[Rule], rules)
        self._policy = self.__class__.__name__
        self._rules = rr or []
        super().__init__(**kwargs)


    @abstractmethod
    def evaluate(self, app) -> Tuple[Decision, dict]: ...

    def policy_selected(self, app):
        self.hash_chain.append({
            "event": "POLICY_SELECTED",
            "id": app.id + "_" + self.id + "_" + datetime.now(UTC).strftime("%Y-%m-%d_%H:%M:%S"),
            "policy": self.id
        })

    def policy_evaluated(self, app):
        self.hash_chain.append({
            "event": "POLICY_EVALUATED",
            "id": app.id + "_" + self.id + "_" + datetime.now(UTC).strftime("%Y-%m-%d_%H:%M:%S"),
            "policy": self.id
        })

    def __str__(self):
        return f"{self.__class__.__name__}(id={self.id}, rules={self.rules_as_strings})"

    @classmethod
    def str_to_rules(cls, rules: Any) -> list[Rule]:
        if Policy.is_list_of_strings(rules):
            r = []
            for s in (rules or []):
                r.append(RULE_REGISTRY[s]())
            return r
        return rules

    @classmethod
    def is_list_of_strings(cls, obj):
        return isinstance(obj, list) and all(isinstance(elem, str) for elem in obj)

    def to_dict(self):
        data = super().to_dict()
        data["rules"] = self.rules_as_strings
        return data

    @classmethod
    def from_dict(cls, hash_chain: HashChain, data: dict, **kwargs) -> Policy:
        obj = POLICY_REGISTRY[data.get("policy")](hash_chain=hash_chain, rules=data.pop("rules"), **data)
        return obj

    def validate(self):
        super().validate()
        emit.emit({
            "event": "POLICY_VALIDATED",
            "id": self.id,
            "date": datetime.now(UTC),
            "data": str(self)
        })

    @property
    def policy(self) -> str:
        return self._policy
    @policy.setter
    def policy(self, policy: str):
        self._policy = policy
        self._updated_at = datetime.now(UTC)

    @property
    def rules(self) -> list[Rule]:
        return self._rules
    @rules.setter
    def rules(self, rules: list[Rule]):
        self._rules = Policy.str_to_rules(rules)
        self._updated_at = datetime.now(UTC)

    @property
    def rules_as_strings(self) -> list[str]:
        rules = self.rules
        if rules and not Policy.is_list_of_strings(rules):
            rules = [r.__class__.__name__ for r in rules]
        return rules
