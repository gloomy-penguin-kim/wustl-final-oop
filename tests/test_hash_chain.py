from __future__ import annotations

from app.audit import EmitEvent
from app.audit.hash_chain import HashChain
from app.persistence import JsonCrud
from app.policies import ScorecardPolicy, RuleBasedPolicy, HybridPolicy
from app.rules import Rule, EmploymentRule, DtiRule, CreditScoreRule
from app.rules import RuleStatus, RuleResult
from app.rules.loan_amount_rule import LoanAmountRule
from app.rules.rule_registry import register_rule  

from app.domain import LoanApplication, Applicant
from app.engine import DecisionEngine  
from app.settings import Config

from decimal import Decimal
import random


@register_rule
class RuleToReturnRefer(Rule):
    def __init__(self):  
        self.code = "RF_TEST"
        self.reason = "refer test for rule codes"

    def apply(self, app, ctx) -> RuleResult:
        result = RuleResult(RuleStatus.REFER, self.code)
        ctx[result.status][self.code] = self.reason  
        return result


@register_rule
class RuleToReturnApproved1(Rule):
    def __init__(self):  
        self.code = "APPRV_1"
        self.reason = "approved test for rule codes 1"

    def apply(self, app, ctx) -> RuleResult:
        result = RuleResult(RuleStatus.APPROVE, self.code)
        ctx[result.status][self.code] = self.reason  
        return result

        
@register_rule
class RuleToReturnApproved2(Rule):
    def __init__(self):  
        self.code = "APPRV_2"
        self.reason = "approved test for rule codes 2"

    def apply(self, app, ctx) -> RuleResult:
        result = RuleResult(RuleStatus.APPROVE, self.code)
        ctx[result.status][self.code] = self.reason  
        return result


@register_rule
class RuleToDecline(Rule):
    def __init__(self):  
        self.code = "DECLINE"
        self.reason = "declined test for rule codes 2"

    def apply(self, app, ctx) -> RuleResult:
        result = RuleResult(RuleStatus.DECLINE, self.code)
        ctx[result.status][self.code] = self.reason  
        return result


def test_hash_chain_events():
    TEST_AUDIT_FILE = "tests/output/test_audit.jsonl"
    hc = HashChain(TEST_AUDIT_FILE)
    hc.clear()
    ee = EmitEvent("tests/output/test_events.jsonl")
    ee.clear()
    jc = JsonCrud("tests/output/test_persistence.jsonl")
    jc.clear()

    sc_policy = ScorecardPolicy(id="testing_tacos_are_soft_tacos")
    ru_policy = RuleBasedPolicy(id="testing_tacos_are_ruly_tacos", rules=[RuleToReturnRefer(), RuleToReturnApproved1()])
    hy_policy = HybridPolicy(id="testing_tacos_are_hybrid_tacos", rules=[RuleToReturnApproved2(), RuleToReturnApproved1(), RuleToDecline()])

    app = LoanApplication(
        applicant=Applicant(
            name="Alice",
            annual_income=Decimal("80000"),
            monthly_debt=Decimal("1500"),
            credit_score=720,
            employment_status="EMPLOYED"
        ),
        requested_amount=Decimal("15000"),
        term_months=36,
        purpose="car",
        id="something_really_specific"
    )
    app.submit()
    app.validate()

    engine = DecisionEngine()
    decision, ctx = engine.run(app, sc_policy)

    assert len(hc.chain) == 5
    assert hc.chain[0]["event"] == "SUBMITTED"
    assert hc.chain[1]["event"] == "VALIDATED"
    assert hc.chain[2]["event"] == "POLICY_SELECTED"
    assert hc.chain[3]["event"] == "POLICY_EVALUATED"
    assert hc.chain[4]["event"] == "DECISIONED"

    app2 = LoanApplication(
        applicant=Applicant(
            name="Bob",
            annual_income=Decimal("20000"),
            monthly_debt=Decimal("300"),
            credit_score=720,
            employment_status="DISABLED"
        ),
        requested_amount=Decimal("90000"),
        term_months=36,
        purpose="car",
        id="APP101023",
    )

    app2.submit()
    app2.validate()
    decision5, ctx5 = engine.run(app2, ru_policy)
    decision6, ctx6 = engine.run(app2, hy_policy)
    decision5, ctx5 = engine.run(app2, sc_policy)
    decision6, ctx6 = engine.run(app, hy_policy)

    lines = [] 
    with open(TEST_AUDIT_FILE, "r") as f:
        lines = f.readlines()
    if lines:  
        idx = random.randrange(1,len(lines)-2)
        removed_line = lines.pop(idx) 
    with open(TEST_AUDIT_FILE, "w") as f:
        f.writelines(lines)

    print("lines in the file", len(lines)) 
    print("removed line", idx, removed_line)
    result = HashChain.verify_chain()
    assert idx == result[1] 
    assert result[0] == False


def test_hash_chain():
     for _ in range(10):
         test_hash_chain_events()
    