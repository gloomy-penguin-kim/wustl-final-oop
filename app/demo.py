from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from app.domain.applicant import Applicant
from app.domain.application import LoanApplication
from app.engine.decision_engine import DecisionEngine
from app.policies.rule_based_policy import RuleBasedPolicy
from app.policies.scorecard_policy import ScorecardPolicy
from app.rules.credit_score_rule import CreditScoreRule
from app.rules.dti_rule import DtiRule 
from app.audit.event_sink import FileEventSink
from app.engine.policy_registry import PolicyRegistry
from app.persistence.json_store import JsonStore
from app.wrappers.loans import Loans
from app.wrappers.policies import Policies


applicant = Applicant(
    "Alice",
    Decimal("80000"),
    Decimal("1500"),
    720,
    "EMPLOYED"
)

 
loans = Loans("loans.jsonl")
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
 
app2 = loans.new( 
    applicant=applicant,
    requested_amount=Decimal("15000"),
    term_months=36,
    purpose="car", 
    application_id="pizza"
)

assert isinstance(app2, LoanApplication)
# loans.new({ "applicant": applicant, "requested_amount": Decimal(15000), "term_months": 36, "purpose": "car"})


policies = Policies("policies.jsonl")
# p = policies.new(version="version123", type="RuleBasedPolicy", rules=[CreditScoreRule(), DtiRule()])
# assert p.version in policies.items 
# assert isinstance(p, RuleBasedPolicy)
# p = policies.new(version="version1234", type="ScorecardPolicy")
# assert p.version in policies.items 
# assert isinstance(p, ScorecardPolicy)
# policy = RuleBasedPolicy(
#     [CreditScoreRule(), DtiRule()],
#     version="v1"
# )  
 
engine = DecisionEngine(loans, policies)

policies.delete("rule_based_123")
policies.delete("scorecard")
policy = policies.new("rule_based_123", "RuleBasedPolicy", [CreditScoreRule(), DtiRule()])
policies.register(ScorecardPolicy("scorecard"))
 

d, trace = policy.evaluate(app) 

decision, ctx = engine.run(app, "rule_based_123")
decision, ctx = engine.run(app, "scorecard")

print(decision.reason_codes) 

events = store.load_events("APP001")

verify_chain(events)


# store.append({
#     "type": "application",
#     "application_id": app.application_id,
#     "data": app.to_dict()
# })
# store.append({
#     "type": "audit",
#     "application_id": app.application_id,
#     "event": "SUBMITTED",
#     "timestamp": now,
#     "hash_prev": "...",
#     "hash_self": "..."
# })