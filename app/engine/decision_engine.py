from __future__ import annotations
from typing import Dict, Tuple, overload

from app.audit.event_sink import EmitEvent 
from app.audit.hash_chain import HashChain
from app.domain.application import LoanApplication
from app.domain.decision import Decision
from app.policies.policy_base import Policy
from app.engine.loans import Loans
from app.engine.policies import Policies

class DecisionEngine():
    #
    # def __init__(self, loans: Loans, policies: Policies, **kwargs):
    #     super().__init__(**kwargs)
    #     self.policies = policies
    #     self.loans = loans

    @overload 
    def run(self, application: str, policy_version: str) -> Tuple[Decision, Dict]: ...
    @overload 
    def run(self, application: LoanApplication, policy_version: str) -> Tuple[Decision, Dict]: ...
    @overload 
    def run(self, application: str, policy_version: Policy) -> Tuple[Decision, Dict]: ...
    @overload 
    def run(self, application: LoanApplication, policy_version: Policy) -> Tuple[Decision, Dict]: ...

    def run(self, application, policy_version) -> Tuple[Decision, Dict]:
        if isinstance(application, str):
            application = LoanApplication.load_from_file(application)
            if not application.is_validated:
                raise ValueError("Loan application is not validated.")
        if isinstance(policy_version, str):
            policy_version = Policy.load_from_file(policy_version)
        return self.run_app_policy(application, policy_version)

    def run_app_policy(self, application: LoanApplication, policy: Policy):
        decision, ctx = policy.evaluate(application) 
        # self.chain_event({
        #     "event": "DECISIONED",
        #     "id": decision.decision_id,
        #     "application_id": application.application_id,
        #     "policy_version": policy.version,
        #     "decision": decision.to_dict()
        # })
        return decision, ctx

    def replay(self, application_id: str, policy_version: str) -> Tuple[Decision, Dict]:
        return self.run(application_id, policy_version)