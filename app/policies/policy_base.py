from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import UTC, datetime
import json
from typing import Any, Tuple, cast

from app.audit import HashChain, EmitEvent
from app.domain.base_entity import BaseEntity
from app.domain.decision import Decision
from app.mixins.validate_policy import ValidatePolicyMixin
from app.policies.policy_registry import POLICY_REGISTRY
from app.rules import Rule
from app.rules import RULE_REGISTRY


class Policy(ValidatePolicyMixin, BaseEntity, ABC):

    def __init__(self,
                 rules: list[Rule] = None,
                 *args,
                 **kwargs):

        kwargs["type"] = "Policy"
        kwargs["policy"] = self.__class__.__name__

        super().__init__(*args, **kwargs)

        self._policy = self.__class__.__name__
        self._rules = rules or []

        self.init(**kwargs)
        self.save()

    @abstractmethod
    def evaluate(self, app) -> Tuple[Decision, dict]: ...

    def _update_id(self, new_id: int, type: str):
        prev_id = self.id
        super()._update_id(new_id, type)
        Policy.delete_from_file_by_id(prev_id)
        self.save()

    def policy_selected(self, app):
        HashChain.append({
            "event": "POLICY_SELECTED",
            "id": app.id + "_" + self.id + "_" + datetime.now(UTC).strftime("%Y-%m-%d_%H:%M:%S"),
            "policy": self.id
        })

    def policy_evaluated(self, app):
        HashChain.append({
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
    def from_dict(cls, data: dict, **kwargs) -> Policy:
        obj = POLICY_REGISTRY[data.get("policy")](rules=data.pop("rules"), **data)
        return obj

    def validate(self):
        self.save()
        super().validate()
        EmitEvent.emit({
            "event": "POLICY_VALIDATED",
            "id": self.id,
            "date": datetime.now(UTC),
            "data": self.to_dict()
        })

    def save(self):
        super().save("Policy")

    @classmethod
    def delete(cls, id: str, type: str="Policy"):
        super().delete(id, type)

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
