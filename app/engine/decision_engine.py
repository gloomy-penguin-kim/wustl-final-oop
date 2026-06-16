from __future__ import annotations
from typing import Dict, Tuple, overload

from app.audit.hash_chain import HashChain
from app.domain.application import LoanApplication
from app.domain.decision import Decision
from app.domain.domain_registry import DOMAIN_REGISTRY
from app.policies.policy_base import Policy
from app.repository.domain_repo import Repository


class DecisionEngine:

    def __init__(self, hash_chain: HashChain, repo: Repository, **kwargs):
        super().__init__(**kwargs)
        self._repo = repo
        self._hash_chain = hash_chain

    @overload 
    def run(self, application: str, policy_version: str) -> Tuple[Decision, Dict]: ...
    @overload 
    def run(self, application: LoanApplication, policy_version: str) -> Tuple[Decision, Dict]: ...
    @overload 
    def run(self, application: str, policy_version: Policy) -> Tuple[Decision, Dict]: ...
    @overload 
    def run(self, application: LoanApplication, policy_version: Policy) -> Tuple[Decision, Dict]: ...

    def run(self, application, policy) -> Tuple[Decision, Dict]:
        if isinstance(application, str):
            application = self._repo.get(application)
            if not application.is_validated:
                raise ValueError("Loan application is not validated.")
        if isinstance(policy, str):
            policy = self._repo.get(policy)
            if not policy.is_validated:
                raise ValueError("Policy is not validated.")
        return self.run_app_policy(application, policy)

    def run_app_policy(self, application: LoanApplication, policy: Policy):
        if not application.is_validated:
            raise ValueError("Loan application is not validated.")
        decision, ctx = policy.evaluate(application)
        self._repo.save(decision)
        self._hash_chain.append({
            "event": "DECISIONED",
            "id": decision.id,
            "application_id": application.id,
            "policy_version": policy.id,
            "decision": decision.to_dict()
        })
        return decision, ctx

    @overload
    def replay_decision(self, application_id: str, policy_version: str) -> Tuple[Decision, Dict]: ...
    @overload
    def replay_decision(self, decision_id: str) -> Tuple[Decision, Dict]: ...

    def replay_decision(self, id1: str, id2: str = None) -> Tuple[Decision, Dict]:
        if id2 is None:
            return self.replay_decision_by_decision(decision_id=id1)
        return self.run(id1, id2)

    def replay_decision_by_decision(self, decision_id: str) -> Tuple[Decision, Dict]:
        decision = self._repo.get(decision_id)
        app = LoanApplication.from_dict(self._hash_chain, decision.application)
        policy = DOMAIN_REGISTRY[decision.policy.get("type")].from_dict(self._hash_chain, data=decision.policy)
        return self.run_app_policy(app, policy)

