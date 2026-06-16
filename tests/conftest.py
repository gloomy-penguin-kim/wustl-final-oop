import uuid

import pytest
from decimal import Decimal

from app.audit import HashChain, EmitEvent
from app.domain import LoanApplication, Applicant
from app.persistence import JsonCrud
from app.policies import HybridPolicy, RuleBasedPolicy, ScorecardPolicy
from app.rules import EmploymentRule, DtiRule, CreditScoreRule
from app.rules.loan_amount_rule import LoanAmountRule


@pytest.fixture
def loan_factory():
    def _make(hc = HashChain("tests/output/test_audit.jsonl")):
        return LoanApplication(
            applicant=Applicant(
                name="Alice",
                annual_income=Decimal("80000"),
                monthly_debt=Decimal("1500"),
                credit_score=720,
                employment_status="EMPLOYED",
                hash_chain=hc,
            ),
            requested_amount=Decimal("15000"),
            term_months=36,
            purpose="car",
            hash_chain=hc
        )
    return _make

@pytest.fixture
def clear_files():
    def _make():
        HashChain("tests/output/test_audit.jsonl").clear()
        EmitEvent("tests/output/test_events.jsonl").clear()
        JsonCrud("tests/output/test_persistence.jsonl").clear()
    return _make


@pytest.fixture
def policy_factory():
    def _make(s: str, hc = HashChain("tests/output/test_audit.jsonl")):
        if s == "hybrid":
            return HybridPolicy(hash_chain=hc, id=str(uuid.uuid4()), rules=[EmploymentRule(), DtiRule(),
                                                                            LoanAmountRule(), CreditScoreRule()])
        elif s == "rulebased":
            return RuleBasedPolicy(hash_chain=hc, id=str(uuid.uuid4()), rules=[EmploymentRule(), DtiRule(),
                                                                            LoanAmountRule(), CreditScoreRule()])
        else:
            return ScorecardPolicy(hash_chain=hc, id=str(uuid.uuid4()))
    return _make
