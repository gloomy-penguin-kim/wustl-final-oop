# demo.py — Composable Credit Decisioning Platform (CCDP)

from decimal import Decimal

from app.audit import EmitEvent, HashChain
from app.domain import LoanApplication, Applicant
from app.engine import DecisionEngine
from app.policies import HybridPolicy, ScorecardPolicy, RuleBasedPolicy
from app.repository.domain_repo import Repository
from app.rules import EmploymentRule, DtiRule, RuleStatus, CreditScoreRule
from app.rules.loan_amount_rule import LoanAmountRule

# =========================================================

# SETUP

# =========================================================

print("\n=== INITIALIZING SYSTEM ===")

HashChain().clear()
EmitEvent().clear()
Repository().clear()

hc = HashChain()
repo = Repository(hc)
engine = DecisionEngine(hc, repo)

# =========================================================

# APPLICATION 1 — HYBRID POLICY DEMO

# =========================================================

print("\n=== APPLICATION 1: HYBRID POLICY ===")

app1 = LoanApplication(
    applicant=Applicant(
        name="Alice",
        annual_income=Decimal("0"),
        monthly_debt=Decimal("1500"),
        credit_score=700,
        employment_status="EMPLOYED",
        hash_chain=hc,
    ),
    requested_amount=Decimal("15000"),
    term_months=36,
    purpose="car",
    hash_chain=hc,
    id="AP444487644"
)

app1.submit()
app1.validate()

repo.add(app1)

# Verify persistence round-trip

print("Verifying persistence...")
app1_copy = repo.get(app1.id)
assert app1.isequal(app1_copy)

# Update ID and persist again

app1.id = "application_id_123"
repo.save(app1)
assert app1.isequal(repo.get(app1.id))

# ---------------------------------------------------------

# Hybrid Policy

# ---------------------------------------------------------

policy1 = HybridPolicy(
    hash_chain=hc,
    id="hybrid_policy_id",
    rules=[EmploymentRule(), DtiRule()]
)

policy1.validate()
repo.add(policy1)

print("Running decision (Hybrid Policy)...")
decision_alice, ctx = engine.run(app1, policy1)

print("Decision:", decision_alice.status)
print("Reason Codes:", decision_alice.reason_codes)

# ---------------------------------------------------------

# Replay Demonstration

# ---------------------------------------------------------

print("\n--- REPLAY DEMONSTRATION ---")

# Mutate application AFTER decision

app1.applicant.credit_score = Decimal(300)
repo.save(app1)

print("Re-running using current repo state (should differ)...")
replay_current, _ = engine.replay_decision(app1.id, policy1.id)
assert not replay_current.isequivalent(decision_alice)

print("Replaying original decision using decision_id...")
replay_original, _ = engine.replay_decision(decision_alice.id)
assert replay_original.isequivalent(decision_alice)

print("Replay successful and deterministic ✔")

# =========================================================

# APPLICATION 2 — SCORECARD POLICY DEMO

# =========================================================

print("\n=== APPLICATION 2: SCORECARD POLICY ===")

app2 = LoanApplication(
    applicant=Applicant(
        name="Bob",
        annual_income=Decimal("22000"),
        monthly_debt=Decimal("500"),
        credit_score=700,
        employment_status="UNEMPLOYED",
        hash_chain=hc,
    ),
    requested_amount=Decimal("15000"),
    term_months=36,
    purpose="car",
    hash_chain=hc,
    id="AP123000112"
)

app2.submit()
app2.validate()

scorecard = ScorecardPolicy(hash_chain=hc, id="scorecard_policy_id")
scorecard.validate()
repo.add(scorecard)

print("Running initial scorecard decision...")
decision_bob_1, _ = engine.run(app2, scorecard)
print("Decision:", decision_bob_1.status)
assert decision_bob_1.status == RuleStatus.APPROVE

# Modify application to trigger different outcome

app2.requested_amount = Decimal("144000")
app2.validate()
repo.save(app2)

print("Running modified decision...")
decision_bob_2, _ = engine.run(app2, scorecard)
print("Decision:", decision_bob_2.status)
assert decision_bob_2.status == RuleStatus.DECLINE

# Replay behavior

print("\n--- REPLAY COMPARISON ---")

print("Replay using current repo state...")
r_current, _ = engine.replay_decision(app2.id, scorecard.id)
assert r_current.status == RuleStatus.DECLINE

print("Replay using decision snapshot (original)...")
r_original, _ = engine.replay_decision(decision_bob_1.id)
assert r_original.status == RuleStatus.APPROVE

print("Restoring application to original state...")
app2.requested_amount = Decimal("15000")
app2.validate()
repo.save(app2)

r_restored, _ = engine.replay_decision(app2.id, scorecard.id)
assert r_restored.status == RuleStatus.APPROVE

print("Replay behavior validated ✔")

# =========================================================

# APPLICATION 3 — RULE-BASED POLICY + EXPORT

# =========================================================

print("\n=== APPLICATION 3: RULE-BASED POLICY + EXPORT ===")

hc2 = HashChain()
repo2 = Repository(hc2)

app3 = LoanApplication(
    applicant=Applicant(
        name="Charlie",
        annual_income=Decimal("100000"),
        monthly_debt=Decimal("1500"),
        credit_score=780,
        employment_status="EMPLOYED",
        hash_chain=hc2,
    ),
    requested_amount=Decimal("41000"),
    term_months=36,
    purpose="car",
    hash_chain=hc2,
    id="AP990009999"
)

app3.submit()
app3.validate()

policy3 = RuleBasedPolicy(
    hash_chain=hc2,
    id="rule_policy_id",
    rules=[CreditScoreRule(), LoanAmountRule()]
)

policy3.validate()

print("Exporting objects to JSONL...")
app3.export("exports.jsonl")
policy3.export("exports.jsonl")
decision_alice.export("exports.jsonl")

print("Export complete ✔")

# =========================================================

# AUDIT VERIFICATION

# =========================================================

print("\n=== AUDIT CHAIN VERIFICATION ===")

valid, index = hc2.verify_chain()
assert valid and index is None

print("Audit chain valid ✔")

# =========================================================

# DEMO COMPLETE

# =========================================================

print("\n=== DEMO COMPLETE: ALL SYSTEMS WORKING ===")
