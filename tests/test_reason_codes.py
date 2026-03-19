from __future__ import annotations
 
from app.rules import Rule
from app.rules import Status, RuleResult
from app.rules.rule_registry import register_rule  

from app.engine import Policies, Loans
from app.domain import LoanApplication
from app.engine import DecisionEngine
from app.settings import Config

Config.AUDIT_FILE = "tests/output/emit_events.jsonl"

from decimal import Decimal

@register_rule
class RuleToReturnRefer(Rule):
    def __init__(self):  
        self.code = "RF_TEST"
        self.reason = "refer test for rule codes"
    def apply(self, app, ctx) -> RuleResult:
        result = RuleResult(Status.REFER, self.code) 
        ctx[result.status][self.code] = self.reason  
        return result

@register_rule
class RuleToReturnApproved1(Rule):
    def __init__(self):  
        self.code = "APPRV_1"
        self.reason = "approved test for rule codes 1"
    def apply(self, app, ctx) -> RuleResult:
        result = RuleResult(Status.APPROVE, self.code) 
        ctx[result.status][self.code] = self.reason  
        return result
        
@register_rule
class RuleToReturnApproved2(Rule):
    def __init__(self):  
        self.code = "APPRV_2"
        self.reason = "approved test for rule codes 2"
    def apply(self, app, ctx) -> RuleResult:
        result = RuleResult(Status.APPROVE, self.code) 
        ctx[result.status][self.code] = self.reason  
        return result
        
@register_rule
class RuleToDecline(Rule):
    def __init__(self):  
        self.code = "DECLINE"
        self.reason = "declined test for rule codes 2"
    def apply(self, app, ctx) -> RuleResult:
        result = RuleResult(Status.DECLINE, self.code) 
        ctx[result.status][self.code] = self.reason  
        return result

def test_reason_codes(): 

    policies = Policies("tests/output/test_policies.jsonl")
    policies.clear() 

    policy12 = policies.new({ "version": "approved_1_2",
                              "type": "RuleBasedPolicy",
                              "rules": [RuleToReturnApproved1(), RuleToReturnApproved2()]})
    policy21 = policies.new("approved_2_1", "RuleBasedPolicy", [RuleToReturnApproved2(), RuleToReturnApproved1()])
    policy_refer = policies.new("refer_policy", "RuleBasedPolicy", [RuleToReturnApproved1(), RuleToReturnRefer(), 
                                                                    RuleToReturnApproved2(), RuleToDecline()])
    policy_declined = policies.new(version="declined",
                                   type="RuleBasedPolicy",
                                   rules=["RuleToReturnApproved1",
                                          "RuleToReturnApproved2",
                                          "RuleToDecline"])

    loans = Loans("tests/output/test_loans.jsonl")
    loans.clear()

    engine = DecisionEngine(loans, policies)

    loan = loans.new({
        "applicant": {
            "name": "Test Applicant",
            "credit_score": 700,
            "annual_income": Decimal("50000"),
            "monthly_debt": Decimal("1000"),
            "employment_status": "employed"
        },
        "requested_amount": Decimal("10000"),
        "term_months": 36,
        "purpose": "debt_consolidation"
    })

    decision1, ctx1 = engine.run(loan, policy12)
    decision2, ctx2 = engine.run(loan, policy21)  
    assert list(decision1._reason_codes) == ["APPRV_1", "APPRV_2"]
    assert list(decision2._reason_codes) == ["APPRV_2", "APPRV_1"]

    decision3, ctx3 = engine.run(loan, policy_refer)
    assert list(decision3.reason_codes) == ["RF_TEST"]

    decision4, ctx4 = engine.run(loan, policy_declined) 
    assert list(decision4.reason_codes) == ["DECLINE"]

    decision5, ctx5 = engine.run(loan, policy12)
    decision6, ctx6 = engine.run(loan, policy12)
    assert decision5.isEqual(decision6) 

    loans.clear()
    policies.clear() 

    assert loan.application_id not in loans.items
    loans = Loans("tests/output/test_loans.jsonl")
    assert loan.application_id not in loans.items
    assert len(Loans.items) == 0 

    assert "approved_1_2" not in policies.items
    assert "approved_2_1" not in policies.items 
    assert "refer_policy" not in policies.items
    assert "declined" not in policies.items

    policies = Policies("tests/output/test_policies.jsonl")
    assert "approved_1_2" not in policies.items 
    assert "approved_2_1" not in policies.items
    assert "refer_policy" not in policies.items
    assert "declined" not in policies.items 
    assert len(Policies.items) == 0
 