from __future__ import annotations

from datetime import datetime
from decimal import Decimal
 
from app.audit import FileEventSink
from app.domain import Applicant
from app.domain import LoanApplication
from app.engine import DecisionEngine
from app.policies import RuleBasedPolicy, ScorecardPolicy 
from app.rules import CreditScoreRule, DtiRule
from app.wrappers import Policies
from app.settings import Config

Config.AUDIT_FILE = "tests/output/emit_events.jsonl"

  

def test_policies(): 
    policies = Policies("tests/output/test_policies.jsonl")
    policies.clear()
    
    policies.new(ScorecardPolicy("testing..."))
    policies.new(RuleBasedPolicy("testing...2", rules=[CreditScoreRule(), DtiRule()]))
    assert "testing..." in policies.items 
    assert "testing...2" in policies.items 

    policies = Policies("tests/output/test_policies.jsonl")
    assert "testing..." in policies.items 
    assert "testing...2" in policies.items 

    policies.clear()
    assert "testing..." not in policies.items 
    assert "testing...2" not in policies.items 

    assert "version123" not in policies.items 
    assert "version1234" not in policies.items 
    assert "version1234" not in policies.items  
    assert "version1234" not in policies.items 
    assert "scorecard_policy" not in policies.items 
    assert "testing..." not in policies.items 
 
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
 
    policies.new({ "version": "scorecard_policy", "type": "ScorecardPolicy" })
    p = policies.get("scorecard_policy")
    assert p.version in policies.items 
    assert isinstance(p, ScorecardPolicy)
 
    policies.delete("version123") 
    assert "version123" not in policies.items 
    assert "version1234" in policies.items 

    policies.delete("version1234") 
    assert "version1234" not in policies.items 
    assert "version12356" in policies.items
    assert "version1235678" in policies.items
    assert "scorecard_policy" in policies.items

    policies.delete("version12356") 
    assert "version1234" not in policies.items  
    assert "version12356" not in policies.items
    assert "version1235678" in policies.items
    assert "scorecard_policy" in policies.items

    policies.delete("version1235678") 
    assert "version1234" not in policies.items 
    assert "version1235678" not in policies.items
    assert "scorecard_policy" in policies.items

    policies.delete("scorecard_policy") 
    assert "scorecard_policy" not in policies.items 
 
def test_policies_duplicates():
    policies = Policies("tests/output/test_policies.jsonl")
    policies.clear()
    
    p = policies.new(version="version123", type="ScorecardPolicy")

    try: 
        p2 = policies.new(version="version123", type="ScorecardPolicy")
        raise AssertionError("should not allow duplicate version") 
    except ValueError as e:
        assert str(e) == "Policy version already exists: version123"
        pass 

    policies.delete("version123") 
    p2 = policies.new(version="version123", type="ScorecardPolicy")

    policies.clear()
     
