from __future__ import annotations
import importlib
import sys
from typing import Any, overload
 

from app.persistence.json_store import JsonStore 
from app.policies.policy_base import Policy
from app.domain.policy_record import PolicyRecord 
from app.rules.rule_base import Rule
from app.wrappers.wrapper import Wrapper
from app.policies.policy_registry import POLICY_REGISTRY
  

class Policies(Wrapper, JsonStore):  
    items = {} 
    def __init__(self, filename: str, **kwargs):
        super().__init__(filename, **kwargs)
        Policies.items = Policies.items | self.load_by_type()

    def register(self, item: Policy) -> None:  
        self._add_item(item)  
    
    @overload 
    def new(self, item: PolicyRecord) -> Policy:...
    def new_from_policy_record(self, item: PolicyRecord) -> Policy:   
        if item.type in POLICY_REGISTRY: 
            policy = POLICY_REGISTRY[item.type](item.version, item.str_to_rules()) 
            self.register(policy)
            return policy
        raise ValueError(f"Invalid Policy Type: {item.type}") 
 
    @overload 
    def new(self, d: dict) -> Policy:...
    def new_from_dict(self, d: dict) -> Policy:
        policy = PolicyRecord(version=d["version"], type=d["type"], rules=d["rules"]) 
        return self.new_from_policy_record(policy)
        
    @overload 
    def new(self, version: str, type: str, rules: list[Rule] | list[str] | None = None) -> Policy:...
    def new_from_params(self, version: str, type: str, rules: list[Rule] | list[str] | None = None) -> Policy:   
        p = PolicyRecord(version, type, rules)   
        return self.new_from_policy_record(p)
  
    def new(self, *args, **kwargs) -> Policy: 
        if args: 
            if len(args) > 0: 
                if isinstance(args[0], dict):
                    return self.new_from_dict(*args)
                elif isinstance(args[0], PolicyRecord):  
                    return self.new_from_policy_record(*args) 
                else:  
                    return self.new_from_params(*args) 
        if len(kwargs) > 1:   
            return self.new_from_params(*args, **kwargs)
        raise ValueError("Incorrect arguments supplied to Policies.new(...)")
     
    @overload
    def _add_item(self, item: Policy) -> None:...
    def _add_item_from_policy(self, item: Policy) -> None:
        self._add_item_from_policy_record(PolicyRecord(item.version, item.type, item.rules))

    @overload
    def _add_item(self, item: PolicyRecord) -> None:...
    def _add_item_from_policy_record(self, item: PolicyRecord) -> None:
        if item.version in Policies.items: 
            raise ValueError(f"Policy version already exists: {item.version}")
        j = {
            "type": "Policies", 
            "id": item.version, 
            "version": item.version, 
            "data": item.to_dict()
            } 
        self.items[item.version] = j
        self.save(j)

    def _add_item(self, item) -> None: 
        if isinstance(item, Policy):
            return self._add_item_from_policy(item)
        elif isinstance(item, PolicyRecord):  
            return self._add_item_from_policy_record(item) 
        raise ValueError("Incorrect arguments supplied to Policies._add_item(...)")
    
    def get(self, id: str) -> Policy:
        if id not in self.items:
            try: 
                policy = self.load_policy(id) 
            except: 
                raise ValueError(f"Policy not found: {id}")
        policy = Policies.items[id] 
        if isinstance(policy, str):
            policy = PolicyRecord.from_json(policy) 
        if isinstance(policy, dict): 
            if "data" in policy: policy = policy["data"] 
            policy = PolicyRecord.from_dict(policy) 
        if isinstance(policy, PolicyRecord):
            policy = self._from_policy_record(policy)
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