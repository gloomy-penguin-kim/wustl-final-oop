from __future__ import annotations
 
from decimal import Decimal

from app.domain import Applicant, LoanApplication
from app.engine import DecisionEngine 
from app.policies import ScorecardPolicy, HybridPolicy, RuleBasedPolicy, Policy
from app.rules import DtiRule, CreditScoreRule
from app.wrappers import Loans
from app.wrappers import Policies
from app.audit import AuditEventSink  
from app.mixins.hash_chain_mixin import HashChainAuditMixin

from .settings import Config
 


applicant = Applicant(
    "Alice",
    Decimal("80000"),
    Decimal("1500"),
    720,
    "EMPLOYED"
)

 
loans = Loans("loans.jsonl")
loans.clear() 

policies = Policies("policies.jsonl")
policies.clear() 

engine = DecisionEngine(loans, policies)


loans.delete("tacobell")
loans.delete("pizza")

app = LoanApplication( 
    applicant=applicant,
    requested_amount=Decimal("15000"),
    term_months=36,
    purpose="car",
    application_id="tacobell"
)

loans.register(app) 
 
applicant = Applicant(
    "Alice",
    Decimal("80000"),
    Decimal("600"),
    720,
    "EMPLOYED"
)

app2 = loans.new( 
    applicant=applicant,
    requested_amount=Decimal("75000"),
    term_months=36,
    purpose="car" 
)

assert isinstance(app2, LoanApplication)
# loans.new({ "applicant": applicant, "requested_amount": Decimal(15000), "term_months": 36, "purpose": "car"})



policies.delete("rule_based_1234444")
policies.delete("rule_based_123")
policies.delete("scorecard")


policy1 = policies.new("rule_based_123", "RuleBasedPolicy", [CreditScoreRule(), DtiRule()])
policy2 = policies.new(ScorecardPolicy("scorecard"))
assert policy1 is not None
assert policy1.type == "RuleBasedPolicy"
assert policy1.version == "rule_based_123"
assert policy1.version in policies.items
assert policy1.rules_as_strings == ['CreditScoreRule', 'DtiRule']
assert isinstance(policy1, Policy)
assert isinstance(policy1, RuleBasedPolicy)
assert "scorecard" in policies.items
assert policy2.version == "scorecard"
assert policy1.version in policies.items
assert len(policy2.rules_as_strings) == 0
assert isinstance(policy2, Policy)
assert isinstance(policy2, ScorecardPolicy)
  
d, trace = policy1.evaluate(app) 

print(1) 
decision, ctx = engine.run(app, policy1)
print(decision.reason_codes) 
print("context", ctx) 

print(2)
policy2 = policies.new("rule_based_1234444", "HybridPolicy", ["CreditScoreRule", "EmploymentRule"])
policy2 = policies.get("rule_based_1234444") 
decision, ctx = engine.run(app.application_id, policy2.version)
print(decision.status)
print(decision.reason_codes)
print("context", ctx) 

print(3) 
decision, ctx = engine.run(app, "scorecard")
print(decision.status)
print(decision.reason_codes)
print("context", ctx)

print(3.1)
decision, ctx = engine.run(app, policy2)
print(decision.status)
print(decision.reason_codes)
print("context", ctx)
print(4) 
decision, ctx = engine.run("tacobell", "scorecard")
print(decision.status)
print(decision.reason_codes)
print("context", ctx)

audit = AuditEventSink()
audit.chain.verify_chain()  
HashChainAuditMixin.verify_chain_in_file() 


policies.clear()
loans.clear() 
  