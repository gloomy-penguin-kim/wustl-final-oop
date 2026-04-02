from __future__ import annotations
 
from decimal import Decimal

from app.audit import EmitEvent, HashChain
from app.domain.applicant import Applicant
from app.domain.application import LoanApplication
from app.engine.decision_engine import DecisionEngine
from app.policies import RuleBasedPolicy, Policy
from app.policies.scorecard_policy import ScorecardPolicy
from app.rules.credit_score_rule import CreditScoreRule
from app.rules.dti_rule import DtiRule  
from app.rules.employment_rule import EmploymentRule
from app.engine import Loans, Policies 

applicant = Applicant(
    "Alice",
    Decimal("80000"),
    Decimal("1500"),
    720,
    "EMPLOYED"
)


LoanApplication.delete("tacobell")

app = LoanApplication(
    applicant=applicant,
    requested_amount=Decimal("15000"),
    term_months=36,
    purpose="car",
    id="tacobell"
)

app_copy = app.copy()
assert app.requested_amount == app_copy.requested_amount
assert app.created_at == app_copy.created_at
assert app.submitted_at == app_copy.submitted_at
assert app.validated_at == app_copy.validated_at
assert app.applicant.name == app_copy.applicant.name
assert app.applicant.isequal(app_copy.applicant)


app.save()

assert app.requested_amount == app_copy.requested_amount
assert app.created_at == app_copy.created_at
assert app.submitted_at == app_copy.submitted_at
assert app.validated_at == app_copy.validated_at
assert app.applicant.name == app_copy.applicant.name
assert app.applicant.isequal(app_copy.applicant)

LoanApplication.delete(app.id)

app.submit()
app.validate()

app2 = LoanApplication(
    applicant={
        "name": "Bob",
        "annual_income": Decimal("15000"),
        "monthly_debt": Decimal("300"),
        "credit_score" : 800,
        "employment_status": "SOCIAL SECURITY"
    },
    requested_amount=Decimal("15000"),
    term_months=36,
    purpose="car",
    id="tacobell"
)

app2.submit()
app_copy = app2.copy()
app2.validate()

assert app2.requested_amount == app_copy.requested_amount
assert app2.created_at == app_copy.created_at
assert app2.submitted_at == app_copy.submitted_at
assert app2.validated_at != app_copy.validated_at
assert app2.applicant.name == app_copy.applicant.name
assert app2.applicant.isequal(app_copy.applicant)


Policy.delete("rule_based_123")

rb_policy = RuleBasedPolicy("rule_based_123", [CreditScoreRule(), DtiRule()])

rb_policy.validate()
rb_policy.save()


engine = DecisionEngine()

decision, ctx = engine.run(app2, rb_policy)

print(decision)

chain = HashChain.verify_chain_in_file()
print(chain)

EmitEvent.clear_sink()


# applicant = Applicant(
#     "Alice",
#     Decimal("80000"),
#     Decimal("1500"),
#     720,
#     "EMPLOYED"
# )
#
#
# loans = Loans("loans.jsonl")
# policies = Policies("policies.jsonl")
# engine = DecisionEngine(loans, policies)
#
# loans.delete("tacobell")
# loans.delete("pizza")
#
# app = LoanApplication(
#     applicant=applicant,
#     requested_amount=Decimal("15000"),
#     term_months=36,
#     purpose="car",
#     application_id="tacobell"
# )
#
# loans.new(app)
#
# applicant = Applicant(
#     "Alice",
#     Decimal("80000"),
#     Decimal("600"),
#     720,
#     "EMPLOYED"
# )
#
# app2 = loans.new(
#     applicant=applicant,
#     requested_amount=Decimal("75000"),
#     term_months=36,
#     purpose="car"
# )
#
# assert isinstance(app2, LoanApplication)
# # loans.new({ "applicant": applicant, "requested_amount": Decimal(15000), "term_months": 36, "purpose": "car"})
#
# credot = {
#     "CreditScoreRule": CreditScoreRule,
#     "DtiRule": DtiRule,
#     "EmploymentRule": EmploymentRule
# }
#
# policies.delete("rule_based_1234444")
# policies.delete("rule_based_123")
# policies.delete("scorecard")
# policy1 = policies.new("rule_based_123", "RuleBasedPolicy", [CreditScoreRule(), DtiRule()])
# policies.new(ScorecardPolicy("scorecard"))
#
# d, trace = policy1.evaluate(app)
#
# print(1)
# decision, ctx = engine.run(app, policy1)
# print(decision.reason_codes)
# print("context", ctx)
#
# policy2 = policies.new("rule_based_1234444", "RuleBasedPolicy", ["CreditScoreRule"])
# policy2 = policies.get("rule_based_1234444")
# decision, ctx = engine.run(app, policy2)
# print(decision.reason_codes)
# print("context", ctx)
#
# print(3)
# decision, ctx = engine.run(app, "scorecard")
# print(decision.reason_codes)
# print("context", ctx)
#
# print(4)
# decision, ctx = engine.run(app2, "scorecard")
# print(decision.reason_codes)
# print("context", ctx)
#
#