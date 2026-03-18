from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal
import sys
from typing import Any, Tuple 

from app.mixins.json_serializable import JsonSerializableMixin 
from app.policies.policy_base import Policy
from app.rules.rule_base import Rule
from app.rules.rule_registry import RULE_REGISTRY


class PolicyRecord(JsonSerializableMixin):
    def __init__(
        self,
        version: str, 
        type: str, 
        rules: Any = None,
        created_at: datetime = datetime.now(UTC)  
    ):
        self.version = version 
        self.type = type 
        self.rules = rules  
        if rules and not PolicyRecord.is_list_of_strings(rules):
            self.rules = [r.__class__.__name__ for r in rules] 
        self.created_at = created_at 
  
        
    @classmethod
    def from_dict(cls, data: dict): 
        data["created_at"] = datetime.fromisoformat(data["created_at"]) if isinstance(data["created_at"], str) else data["created_at"]
        data["rules"] = [RULE_REGISTRY[r]() for r in data["rules"]]

        return cls(**data) 
    
    @classmethod
    def from_policy(cls, policy: Policy):

        data = {} 
        data["version"] = policy.version
        data["type"] = policy.type 
        data["rules"] = policy.rules 
        data["created_at"] = datetime.now(UTC)
        
        if policy.rules and not PolicyRecord.is_list_of_strings(policy.rules):
            data["rules"] = [r.__class__.__name__ for r in policy.rules]

        return cls(**data)
       
    def str_to_rules(self) -> list[Rule]: 
        r = []  
        for s in (self.rules or []): 
            r.append(RULE_REGISTRY[s]())
        return r 
      
    @classmethod
    def is_list_of_strings(cls, obj):
        return isinstance(obj, list) and all(isinstance(elem, str) for elem in obj)

    
