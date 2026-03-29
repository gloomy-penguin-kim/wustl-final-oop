from __future__ import annotations
import json
from datetime import datetime, UTC
from typing import Any, overload
 

from app.audit import EmitEvent
from app.audit.hash_chain import HashChain
from app.persistence.json_store import JsonStore 
from app.policies.policy_base import Policy 
from app.rules.rule_base import Rule
from app.engine.wrapper import Wrapper
from app.policies.policy_registry import POLICY_REGISTRY
  

class Policies(Wrapper, JsonStore, EmitEvent, HashChain):

    items = dict()

    def __init__(self, 
                 filename: str,   
                 **kwargs):
        super().__init__(filename=filename,  
                         **kwargs)
        self.filename = filename 
        Policies.items = Policies.items | self.load_by_type()
  
    def register(self, policy: Policy):
        self._add_item(policy)
        return policy
 
    @overload 
    def new(self, policy: dict) -> Policy: ...

    @overload
    def new(self, policy: Policy) -> Policy: ...

    def new_from_policy(self, policy: Policy) -> Policy:
        self._add_item(policy)
        return policy
 
    @overload 
    def new(self, policy: dict) -> Policy: ...

    def new_from_dict(self, policy: dict) -> Policy:
        return self.new_from_params(policy.get("version",""),
                                    policy.get("type", ""),
                                    policy.get("rules",[]),
                                    policy.get("created_at", datetime.now(UTC)))
        
    @overload
    def new(self,
            version: str,
            type: str,
            rules: Any = None,
            created_at: datetime | None = None
            ) -> Policy: ...

    def new_from_params(self,
                        version: str,
                        type: str,
                        rules: list[Rule] | list[str] | None = None,
                        created_at: datetime | None = None
                        ) -> Policy:
        created_at = created_at or datetime.now(UTC)
        if type in POLICY_REGISTRY:
            policy = POLICY_REGISTRY[type](version, Policy.str_to_rules(rules), created_at)
            self._add_item(policy)
            return policy
        raise ValueError(f"Invalid Policy Type: {type}")
  
    def new(self, *args, **kwargs) -> Policy: 
        if args: 
            if len(args) > 0: 
                if isinstance(args[0], dict):
                    return self.new_from_dict(*args)
                elif isinstance(args[0], Policy):
                    return self.new_from_policy(*args, **kwargs)
                else:  
                    return self.new_from_params(*args, **kwargs)
        if len(kwargs) > 1:   
            return self.new_from_params(*args, **kwargs)
        raise ValueError("Incorrect arguments supplied to Policies.new(...)")

    def _add_item(self, item: Policy):
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

    def get(self, id: str) -> Any:
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
                policy = POLICY_REGISTRY[policy.get("type","")](policy.get("version"),
                                                             policy.get("rules"),
                                                             policy.get("created_at", datetime.now(UTC))) 
        return policy

    @overload
    def delete(self, policy: Policy): ...
    @overload
    def delete(self, policy: str): ...

    def delete(self, policy: Any) -> None:
        if isinstance(policy, Policy):
            policy = policy.version
        self.delete_policy(policy)

    def delete_policy(self, policy: str):
        if policy in Policies.items:  
            self.update_file(Policies.items) 
            del Policies.items[policy]

    def clear(self): 
        self.clear_file() 
        Policies.items = dict()