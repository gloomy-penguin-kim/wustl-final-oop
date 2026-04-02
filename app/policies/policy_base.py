from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import UTC, datetime
import json
from typing import Any, Tuple, cast

from app.audit import HashChain, EmitEvent
from app.domain.base import BaseEntity
from app.domain.decision import Decision 
from app.mixins.json_serializable import JsonSerializableMixin
from app.mixins.validate_policy import ValidatePolicyMixin
from app.policies.policy_registry import POLICY_REGISTRY
from app.rules import Rule
from app.rules import RULE_REGISTRY


class Policy(ValidatePolicyMixin, JsonSerializableMixin, BaseEntity, ABC):

    def __init__(self,
                 rules: list[Rule] = None,
                 **kwargs):
        super().__init__(**kwargs)

        self._policy = self.__class__.__name__

        self._rules = rules or []
        kwargs["type"] = "Policy"
        kwargs["policy"] = self.__class__.__name__

        self.init(**kwargs)

        assert self.type == "Policy"
        assert self.policy == self.__class__.__name__
        self.save()

    @abstractmethod
    def evaluate(self, app) -> Tuple[Decision, dict]: ...

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
        print("data", data)
        ### this is why the function is here ###
        data["rules"] = self.rules_as_strings
        ########################################
        # data["id"] = self.id
        # data["type"] = "Policy"
        # data["created_at"] = self.created_at
        # data["validated_at"] = self.validated_at
        # data["updated_at"] = self.updated_at
        return data

    @classmethod
    def from_dict(cls, data: dict, **kwargs) -> Policy:
        created_at = data.get("created_at", datetime.now(UTC))
        created_at = datetime.fromisoformat(created_at) if isinstance(created_at, str) else created_at

        validated_at = data.get("validated_at", None)
        validated_at = datetime.fromisoformat(validated_at) if isinstance(validated_at, str) else validated_at

        updated_at = data.get("updated_at", created_at)
        updated_at = datetime.fromisoformat(updated_at) if isinstance(updated_at, str) else updated_at

        kwargs.update({"id": data.get("id"),
                       "created_at": created_at,
                       "validated_at": validated_at,
                       "updated_at": updated_at})

        return (POLICY_REGISTRY[data.get("policy")]
                (rules=data.get("rules"), **kwargs))

    def validate(self):
        super().validate()
        print("VALIDATE", self.__class__.__name__)
        self.save()

    def save(self):
        self.save_to_file(type="Policy")

    @classmethod
    def delete(cls, id: str):
        cls.delete_from_file_by_id(id, "Policy")


    @property
    def policy(self) -> str:
        return self._policy
    @policy.setter
    def policy(self, policy: str):
        self._policy = policy
        self.updated_at = datetime.now(UTC)

    @property
    def rules(self) -> list[Rule]:
        return self._rules
    @rules.setter
    def rules(self, rules: list[Rule]):
        self._rules = rules
        self.updated_at = datetime.now(UTC)

    @property
    def rules_as_strings(self) -> list[str]:
        rules = self.rules
        if rules and not Policy.is_list_of_strings(rules):
            rules = [r.__class__.__name__ for r in rules]
        return rules
