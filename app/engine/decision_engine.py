from __future__ import annotations

from app.audit.event_sink import EmitEvent 
from app.domain.application import LoanApplication
from app.wrappers.loans import Loans
from app.wrappers.policies import Policies 

class DecisionEngine(EmitEvent):

    def __init__(self, loans: Loans, policies: Policies): 
        self.policies = policies 

    # def __init__(self, registry: PolicyRegistry, audit_sink: FileEventSink):

    #     self.registry = registry
    #     self.audit_sink = audit_sink 

    def run(self, application: LoanApplication, policy_version: str):


        policy = self.policies.get(policy_version)

        self.emit({
            "event": "POLICY_SELECTED",
            "id": application.application_id,
            "policy_version": policy_version,
            "policy": policy.to_dict() 
        })

        decision, ctx = policy.evaluate(application)


        self.emit({
            "event": "DECISIONED",
            "id": application.application_id,
            "policy_version": policy_version,
            "decision": decision.to_dict()
        })

        return decision, ctx