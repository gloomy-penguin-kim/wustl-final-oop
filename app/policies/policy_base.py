from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import UTC, datetime
import json
from typing import Any, Tuple, cast

from app.audit import HashChain, EmitEvent
from app.domain.decision import Decision 
from app.mixins.json_serializable import JsonSerializableMixin
from app.mixins.validate_policy import ValidatePolicyMixin
from app.persistence import JsonCrud
from app.policies.policy_registry import POLICY_REGISTRY
from app.rules import Rule
from app.rules import RULE_REGISTRY
from app.settings import Config


class Policy(JsonCrud, ValidatePolicyMixin, JsonSerializableMixin, ABC):

    def __init__(self,  
                 version: str,
                 rules: list[Rule] = None,
                 created_at: datetime = None,
                 validated_at: datetime = None,
                 id: str = None,
                 **kwargs):
        super().__init__(**kwargs)

        JsonCrud.duplicate_check(version, "Policy")

        self._version = version 
        self._type = self.__class__.__name__
        self._rules = rules or [] 
        self._created_at = created_at or datetime.now(UTC)
        self._validated_at = validated_at
        self._id = id or version

        self.save()

        if not created_at:
            EmitEvent.emit(event={
                "event": "Policy Created",
                "date": datetime.now(UTC),
                "data": str(self),
                "id": self.id
            })
         
    @abstractmethod
    def evaluate(self, app) -> Tuple[Decision, dict]: ...


    def policy_selected(self, app):
        HashChain.append({
            "event": "POLICY_SELECTED",
            "id": app.application_id + "_" + self.version + "_" + datetime.now(UTC).strftime("%Y-%m-%d_%H:%M:%S"),
            "policy_version": self.version
        })

    def policy_evaluated(self, app):
        HashChain.append({
            "event": "POLICY_EVALUATED",
            "id": app.application_id + "_" + self.version + "_" + datetime.now(UTC).strftime("%Y-%m-%d_%H:%M:%S"),
            "policy_version": self.version
        })

    def __str__(self):
        return f"{self.__class__.__name__}(version={self.version}, rules={self.rules_as_strings})"

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
        data = dict()
        data["version"] = self.version
        ### this is why the function is here ###
        data["rules"] = self.rules_as_strings
        ########################################
        data["type"] = self.type
        data["created_at"] = self.created_at
        return data

    @classmethod
    def from_dict(cls, data: dict) -> Policy:
        created_at = data.get("created_at", datetime.now(UTC))
        created_at = created_at if isinstance(created_at, datetime) else datetime.fromisoformat(created_at)
        validated_at = data.get("validated_at", None)
        validated_at = datetime.fromisoformat(validated_at) if isinstance(validated_at, str) else None
        return POLICY_REGISTRY[data.get("type")](data.get("version"),
                                                 data.get("rules"),
                                                 created_at=created_at,
                                                 validated_at=validated_at)


    def save(self):
        self.save_to_file(type="Policy")

    @classmethod
    def delete(cls, application_id):
        cls.delete_from_file_by_id(application_id)

    @property
    def id(self) -> str:
        return self._id

    @property
    def version(self) -> str:
        return self._version

    @version.setter
    def version(self, version: str):
        Policy.duplicate_check(version)
        self._version = version

    @property
    def type(self) -> str:
        return self._type

    @type.setter
    def type(self, type: str):
        self._type = type

    @property
    def rules(self) -> list[Rule]:
        return self._rules

    @rules.setter
    def rules(self, rules: list[Rule]):
        self._rules = rules

    @property
    def created_at(self) -> datetime:
        return self._created_at

    @property
    def validated_at(self) -> datetime:
        return self._validated_at

    @validated_at.setter
    def validated_at(self, validated_at: datetime):
        self._validated_at = validated_at

    @property
    def rules_as_strings(self) -> list[str]:
        rules = self.rules
        if rules and not Policy.is_list_of_strings(rules):
            rules = [r.__class__.__name__ for r in rules]
        return rules
