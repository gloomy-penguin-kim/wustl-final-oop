from __future__ import annotations

from app.audit import EmitEvent
from app.audit.hash_chain import HashChain
from app.persistence import JsonCrud
from app.policies import ScorecardPolicy, RuleBasedPolicy, HybridPolicy
from app.repository.domain_repo import Repository
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


def test_hash_chain_events(clear_files, loan_factory):
    TEST_AUDIT_FILE = "tests/output/test_audit.jsonl"
    clear_files()
    hc = HashChain(TEST_AUDIT_FILE)
    assert hc.filename == TEST_AUDIT_FILE

    sc_policy = ScorecardPolicy(hash_chain=hc,
                                id="testing_tacos_are_soft_tacos")
    ru_policy = RuleBasedPolicy(hash_chain=hc,
                                id="testing_tacos_are_ruly_tacos",
                                rules=[RuleToReturnRefer(),
                                       RuleToReturnApproved1()])
    hy_policy = HybridPolicy(hash_chain=hc,
                             id="testing_tacos_are_hybrid_tacos",
                             rules=[RuleToReturnApproved2(),
                                    RuleToReturnApproved1(),
                                    RuleToDecline()])
    assert sc_policy.hash_chain.filename == TEST_AUDIT_FILE
    app = loan_factory(hc)
    app.id = "something_really_specific"
    app.submit()
    app.validate()

    repo = Repository(hash_chain=hc, filename="tests/output/test_persistence.jsonl")
    engine = DecisionEngine(hash_chain=hc, repo=repo)
    decision, ctx = engine.run(app, sc_policy)

    assert hc.chain[0]["event"] == "SUBMITTED"
    assert hc.chain[1]["event"] == "VALIDATED"
    assert hc.chain[2]["event"] == "POLICY_SELECTED"
    assert hc.chain[3]["event"] == "POLICY_EVALUATED"
    assert hc.chain[4]["event"] == "DECISIONED"
    assert len(hc.chain) == 5

    app2 = loan_factory(hc)
    app2.id = "APP101023"

    app2.submit()
    app2.validate()
    repo.save(app2)
    repo.save(ru_policy)
    repo.save(hy_policy)
    repo.save(sc_policy)
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
    result = hc.verify_chain()
    assert idx == result[1] 
    assert result[0] == False


def test_hash_chain(clear_files, loan_factory):
     for _ in range(10):
         test_hash_chain_events(clear_files, loan_factory)
    