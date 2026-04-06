from __future__ import annotations

from app.audit import EmitEvent, HashChain
from app.persistence import JsonCrud
from app.policies import RuleBasedPolicy, HybridPolicy
from app.rules import Rule
from app.rules import RuleStatus, RuleResult
from app.rules.rule_registry import register_rule  

from app.domain import LoanApplication
from app.engine import DecisionEngine
from app.settings import Config

Config.AUDIT_FILE = "tests/output/test_audit.jsonl"
Config.EVENTS_FILE_FILE = "tests/output/test_events.jsonl"

from decimal import Decimal


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

def test_reason_codes():
    hc = HashChain("tests/output/test_audit.jsonl")
    hc.clear()
    ee = EmitEvent("tests/output/test_events.jsonl")
    ee.clear()
    jc = JsonCrud("tests/output/test_persistence.jsonl")
    jc.clear()

    policy12 = RuleBasedPolicy(id="approved_1_2",
                               rules=[RuleToReturnApproved1(), RuleToReturnApproved2()])
    policy21 = RuleBasedPolicy(id="approved_2_1",
                                rules=[RuleToReturnApproved2(), RuleToReturnApproved1()])
    policy_refer = RuleBasedPolicy(id="refer_policy",
                                rules=[RuleToReturnApproved1(), RuleToReturnRefer(),
                                            RuleToReturnApproved2(), RuleToDecline()])
    policy_declined = RuleBasedPolicy(id="declined",
                                rules=["RuleToReturnApproved1",
                                        "RuleToReturnApproved2",
                                        "RuleToDecline"])

    engine = DecisionEngine()

    loan = LoanApplication.from_dict({
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
    loan.submit()
    loan.validate()

    decision1, ctx1 = engine.run(loan, policy12)
    decision2, ctx2 = engine.run(loan, policy21)  
    assert list(decision1._reason_codes) == ["APPRV_1", "APPRV_2"]
    assert list(decision2._reason_codes) == ["APPRV_2", "APPRV_1"]
    assert decision1.reason_codes == decision1.reason_codes

    decision3, ctx3 = engine.run(loan, policy_refer)
    assert list(decision3.reason_codes) == ["RF_TEST"]

    decision4, ctx4 = engine.run(loan, policy_declined) 
    assert list(decision4.reason_codes) == ["DECLINE"]

    decision1, ctx1 = engine.run(loan, policy21)
    decision2, ctx2 = engine.run(loan, policy21)
    assert decision1.isequivalent(decision2)


