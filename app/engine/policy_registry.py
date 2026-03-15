from enum import Enum
import sys

from app.persistence.json_store import JsonStore 
from app.policies.policy_base import Policy
from app.rules.rule_base import Rule
from app.policies.rule_based_policy import RuleBasedPolicy
from app.policies.scorecard_policy import ScorecardPolicy 


class PolicyRegistry:

    def __init__(self, json_store: JsonStore): 
        self.json_store = json_store 
        self._policies = self.json_store.load_policies()
 
# store.append({
#     "type": "application",
#     "application_id": app.application_id,
#     "data": app.to_dict()
# })
    def get(self, version: str) -> Policy:
        if version in self._policies:  
            d = self.json_store.load_policy(version)  
            rules = [self.str_to_class(r) for r in d["rules"]]
            return self.new(d["version"], d["type"], rules)
        raise ValueError("Policy not found")
    
    def new(self, version: str, type: str, rules: list[Rule] | None = None) -> Policy:
        if type == "RuleBasedPolicy": 
            p = RuleBasedPolicy(version, rules)
        else:       
            p = ScorecardPolicy(version) 
        j = {
            "type": "Policy", 
            "id": p.version, 
            "data": { 
                "type": p.type,
                "version": p.version, 
                "rules": [r.__class__.__name__ for r in p.rules] 
            }}
        self._policies[version] = j
        self.json_store.append(j)
        return p  
        
    def str_to_class(self, classname: str):
        return getattr(sys.modules[__name__], classname) 