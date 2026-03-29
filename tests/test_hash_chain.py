from __future__ import annotations
 
from app.audit.hash_chain import HashChain
from app.rules import Rule
from app.rules import Status, RuleResult
from app.rules.rule_registry import register_rule  

from app.engine import Policies, Loans
from app.domain import LoanApplication
from app.engine import DecisionEngine  
from app.settings import Config

from decimal import Decimal
import random

TEST_FILE = "tests/output/test_audit.jsonl"

Config.AUDIT_FILE = TEST_FILE
Config.EVENTS_FILE_FILE = "tests/output/test_events.jsonl"

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


def test_hash_chain_events(): 

    with open(TEST_FILE, "w") as f:
        f.write("")

    audit = HashChain()

    policies = Policies("tests/output/test_loans.jsonl")
    policies.clear() 
    policies.clear_sink() 

    policy12 = policies.new(version="approved_1_2", type="RuleBasedPolicy", rules=[RuleToReturnApproved1(), RuleToReturnApproved2()])
    policy21 = policies.new("approved_2_1", "RuleBasedPolicy", [RuleToReturnApproved2(), RuleToReturnApproved1()])
    policy_refer = policies.new("refer_policy", "RuleBasedPolicy", [RuleToReturnApproved1(), RuleToReturnRefer(), 
                                                                    RuleToReturnApproved2(), RuleToDecline()])
    policy_declined = policies.new("declined", "RuleBasedPolicy", ["RuleToReturnApproved1", "RuleToReturnApproved2", "RuleToDecline"])

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

    print("----------------------", len(audit.chain))
    
    assert loan.application_id == HashChain.chain[-1].get("id", "")
    assert "SUBMITTED" == HashChain.chain[-1].get("event", "") 

    decision1, ctx1 = engine.run(loan, policy12) 
    assert "DECISIONED" == audit.chain[-1].get("event", "") 
    assert loan.application_id == audit.chain[-1].get("application_id", "")
    assert policy12.version == audit.chain[-1].get("policy_version", "")

    decision2, ctx2 = engine.run(loan, policy21)   
    assert "DECISIONED" == audit.chain[-1].get("event", "") 
    assert loan.application_id == audit.chain[-1].get("application_id", "")
    assert policy21.version == audit.chain[-1].get("policy_version", "")

    decision3, ctx3 = engine.run(loan, policy_refer) 
    assert "DECISIONED" == audit.chain[-1].get("event", "") 
    assert loan.application_id == audit.chain[-1].get("application_id", "")
    assert policy_refer.version == audit.chain[-1].get("policy_version", "")

    decision4, ctx4 = engine.run(loan, policy_declined)  
    assert "DECISIONED" == audit.chain[-1].get("event", "") 
    assert loan.application_id == audit.chain[-1].get("application_id", "")
    assert policy_declined.version == audit.chain[-1].get("policy_version", "")

    decision5, ctx5 = engine.run(loan, policy12)
    decision6, ctx6 = engine.run(loan, policy12) 

    lines = [] 
    with open(TEST_FILE, "r") as f:
        lines = f.readlines()
    if lines:  
        idx = random.randrange(1,len(lines)-2)
        removed_line = lines.pop(idx) 
    with open(TEST_FILE, "w") as f:
        f.writelines(lines)

    print("lines in the file", len(lines)) 
    print("removed line", idx)
    result = audit.verify_chain()
    assert idx == result[1] 
    assert result[0] == False
 
    idx = random.randrange(1,len(audit.chain)-2)
    audit.chain.pop(idx)
    result = audit.verify_chain()

    print("lines in the file", len(audit.chain))
    print("removed line", idx)
    assert idx == result[1] 
    assert result[0] == False

    loans.clear()
    policies.clear() 
    with open(TEST_FILE, "w") as f:
        f.write("")
 
    