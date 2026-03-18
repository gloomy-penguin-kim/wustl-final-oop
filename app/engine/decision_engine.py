from __future__ import annotations
from typing import Dict, Tuple, overload

from app.audit.event_sink import EmitEvent 
from app.domain.application import LoanApplication
from app.domain.decision import Decision
from app.policies.policy_base import Policy
from app.wrappers.loans import Loans
from app.wrappers.policies import Policies 

class DecisionEngine(EmitEvent):

    def __init__(self, loans: Loans, policies: Policies): 
        self.policies = policies 
        self.loans = loans 
 
    @overload 
    def run(self, application: str, policy_version: str):...  
    @overload 
    def run(self, application: LoanApplication, policy_version: str):...  
    @overload 
    def run(self, application: str, policy_version: Policy):...  
    @overload 
    def run(self, application: LoanApplication, policy_version: Policy):...  

    def run_app_policy(self, application: LoanApplication, policy: Policy):  
        self.emit({
            "event": "POLICY_SELECTED",
            "id": application.application_id,
            "policy_version": policy.version,
            "policy": policy.to_dict() 
        }) 
        decision, ctx = policy.evaluate(application) 
        self.emit({
            "event": "DECISIONED",
            "id": application.application_id,
            "policy_version": policy.version,
            "decision": decision.to_dict()
        }) 
        return decision, ctx
    
    def run(self, application, policy_version) -> Tuple[Decision, Dict]:  
        if isinstance(application, str):
            application = self.loans.get(application)
        if isinstance(policy_version, str):
            policy_version = self.policies.get(policy_version)
        return self.run_app_policy(application, policy_version)
        
             
