from __future__ import annotations
import importlib
import json
import sys
from typing import Any, overload
 

from app.persistence.json_store import JsonStore 
from app.policies.policy_base import Policy
from app.domain.policy_record import PolicyRecord 
from app.rules.rule_base import Rule
from app.wrappers.wrapper import Wrapper
from app.policies.policy_registry import POLICY_REGISTRY
  

class Policies(Wrapper, JsonStore):  
    items = dict()
    def __init__(self, filename: str, **kwargs):
        super().__init__(filename, **kwargs)
        Policies.items = Policies.items | self.load_by_type()

    def register(self, policy: Policy) -> None:
        self._add_item(policy)

    @overload
    def new(self, policy: Policy) -> Policy:...
    def new_from_policy(self, policy: Policy) -> Policy:
        self._add_item(policy)
        return policy
 
    @overload 
    def new(self, policy: dict) -> Policy:...
    def new_from_dict(self, policy: dict) -> Policy:
        return self.new_from_params(policy.get("version"), policy.get("type"),
                                    policy.get("rules"),)
        
    @overload
    def new(self, version: str, type: str, rules: list[Rule] | list[str] | None = None) -> Policy:...
    def new_from_params(self,
                        version: str,
                        type: str,
                        rules: list[Rule] | list[str] | None = None) -> Policy:
        if type in POLICY_REGISTRY:
            policy = POLICY_REGISTRY[type](version, Policy.str_to_rules(rules))
            self._add_item(policy)
            return policy
        raise ValueError(f"Invalid Policy Type: {type}")
  
    def new(self, *args, **kwargs) -> Policy: 
        if args: 
            if len(args) > 0: 
                if isinstance(args[0], dict):
                    return self.new_from_dict(*args)
                elif isinstance(args[0], Policy):
                    return self.new_from_policy(*args)
                else:  
                    return self.new_from_params(*args) 
        if len(kwargs) > 1:   
            return self.new_from_params(*args, **kwargs)
        raise ValueError("Incorrect arguments supplied to Policies.new(...)")

    def _add_item(self, policy: Policy):
        if policy.version in Policies.items:
            raise ValueError(f"Policy version already exists: {policy.version}")
        j = {
            "type": "Policies",
            "id": policy.version,
            "version": policy.version,
            "data": policy.to_dict()
            }
        self.items[policy.version] = j
        self.save(j)

    def get(self, id: str) -> Policy:
        if id not in Policies.items:
            item = self.load_one(id)
            if item:
                Policies.items[id] = item
            else:
                raise ValueError(f"Policy not found: {id}")
        policy = Policies.items[id] 
        if isinstance(policy, str):
            policy = json.loads(policy)
        if isinstance(policy, dict): 
            if "data" in policy: policy = policy["data"]
            if policy.get("type") in POLICY_REGISTRY:
                policy = POLICY_REGISTRY[policy.get("type")](policy.get("version"), policy.get("rules"))
        return policy 
     
    def _from_policy_record(self, item: PolicyRecord) -> Policy:
        if item.type in POLICY_REGISTRY:
            policy = POLICY_REGISTRY[item.type](item.version, item.str_to_rules())
            return policy
        raise ValueError(f"Invalid Policy Type: {item.type}")
   
    @overload
    def delete(self, item: Policy):... 
    @overload
    def delete(self, item: str):...

    def delete(self, item: Any) -> None:
        if isinstance(item, Policy):
            item = item.version
        self.delete_policy(item)

    def delete_policy(self, item: str):
        if item in Policies.items:  
            self.update_file(Policies.items) 
            del Policies.items[item]

    def clear(self): 
        self.clear_file() 
        Policies.items = {}