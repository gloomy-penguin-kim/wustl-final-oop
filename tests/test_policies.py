from __future__ import annotations

from datetime import datetime
from decimal import Decimal
 
from app.audit.event_sink import FileEventSink
from app.domain.applicant import Applicant
from app.domain.application import LoanApplication
from app.engine.decision_engine import DecisionEngine
from app.policies.rule_based_policy import RuleBasedPolicy
from app.policies.scorecard_policy import ScorecardPolicy
from app.rules.credit_score_rule import CreditScoreRule
from app.rules.dti_rule import DtiRule
from app.wrappers.policies import Policies


def test_policy(): 
    
    applicant = Applicant(
        "Alice",
        Decimal("80000"),
        Decimal("1500"),
        720,
        "EMPLOYED"
    )
    

    app = LoanApplication( 
        applicant,
        Decimal("15000"),
        36,
        "car"
    )

    # policy = RuleBasedPolicy(
    #     [CreditScoreRule(), DtiRule()],
    #     version="v1"
    # )


    # engine = DecisionEngine(policy, FileEventSink("audit.log"))

    # decision = engine.run(app, "v1")

    # print(decision.reason_codes)

def test_policies(): 
    policies = Policies("test_policies.jsonl")
    
    policies.delete("version1235678") 
    policies.delete("version12356") 
    policies.delete("version1234") 
    policies.delete("version123") 
    policies.delete("scorecard_policy") 
 
    p = policies.new(version="version123", type="RuleBasedPolicy", rules=[CreditScoreRule(), DtiRule()])
    assert p.version in policies.items 
    assert isinstance(p, RuleBasedPolicy)
    p = policies.get("version123")
    for x in (p.rules or []): 
        assert x.__class__.__name__ in ["CreditScoreRule", "DtiRule"] 
 
    p = policies.new(version="version1234", type="ScorecardPolicy")
    assert p.version in policies.items 
    assert isinstance(p, ScorecardPolicy) 
    
    p = policies.new("version12356", "RuleBasedPolicy", [CreditScoreRule(), DtiRule()])
    assert p.version in policies.items 
    assert isinstance(p, RuleBasedPolicy)
    
    p = policies.new("version1235678", "RuleBasedPolicy", ["CreditScoreRule", "DtiRule"])
    assert p.version in policies.items 
    assert isinstance(p, RuleBasedPolicy)
 
    policies.register(ScorecardPolicy("scorecard_policy"))
    p = policies.get("scorecard_policy")
    assert p.version in policies.items 
    assert isinstance(p, ScorecardPolicy)
 
    policies.delete("version123") 
    assert "version123" not in policies.items 
    policies.delete("version1234") 
    assert "version1234" not in policies.items 
    policies.delete("version12356") 
    assert "version1234" not in policies.items  
    policies.delete("version1235678") 
    assert "version1234" not in policies.items 
    policies.delete("scorecard_policy") 
    assert "scorecard_policy" not in policies.items 
 