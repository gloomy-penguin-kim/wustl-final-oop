import pytest
from decimal import Decimal

from app.audit import HashChain, EmitEvent
from app.engine import DecisionEngine
from app.repository.domain_repo import Repository
from app.rules import RuleStatus


# =========================================================
# BASIC ENGINE RUN TEST
# =========================================================

def test_engine_runs_with_hybrid_policy(loan_factory, policy_factory, clear_files):
    clear_files()

    hc = HashChain("tests/output/test_audit.jsonl")
    repo = Repository(hc)
    engine = DecisionEngine(hc, repo)

    app = loan_factory(hc)
    app.submit()
    app.validate()
    repo.add(app)

    policy = policy_factory("hybrid", hc)
    policy.validate()
    repo.add(policy)

    decision, ctx = engine.run(app, policy)

    assert decision is not None
    assert isinstance(ctx, dict)


# =========================================================
# POLICY POLYMORPHISM TEST
# =========================================================

@pytest.mark.parametrize("ptype", ["hybrid", "rulebased", "scorecard"])
def test_engine_supports_multiple_policies(ptype, loan_factory, policy_factory, clear_files):
    clear_files()

    hc = HashChain("tests/output/test_audit.jsonl")
    repo = Repository(hc)
    engine = DecisionEngine(hc, repo)

    app = loan_factory(hc)
    app.submit()
    app.validate()
    repo.add(app)

    policy = policy_factory(ptype, hc)
    policy.validate()
    repo.add(policy)

    decision, _ = engine.run(app, policy)

    assert decision is not None


# =========================================================
# REPLAY — DETERMINISTIC USING DECISION_ID
# =========================================================

def test_replay_by_decision_id_is_deterministic(loan_factory, policy_factory, clear_files):
    clear_files()

    hc = HashChain("tests/output/test_audit.jsonl")
    repo = Repository(hc)
    engine = DecisionEngine(hc, repo)

    app = loan_factory(hc)
    app.submit()
    app.validate()
    repo.add(app)

    policy = policy_factory("hybrid", hc)
    policy.validate()
    repo.add(policy)

    decision, _ = engine.run(app, policy)

    # mutate AFTER decision
    app.applicant.credit_score = Decimal(300)
    repo.save(app)

    replayed, _ = engine.replay_decision(decision.id)

    assert replayed.isequivalent(decision)


# =========================================================
# REPLAY — USING CURRENT STATE (NON-DETERMINISTIC)
# =========================================================

def test_replay_by_ids_uses_current_state(loan_factory, policy_factory, clear_files):
    clear_files()

    hc = HashChain("tests/output/test_audit.jsonl")
    repo = Repository(hc)
    engine = DecisionEngine(hc, repo)

    app = loan_factory(hc)
    app.submit()
    app.validate()
    repo.add(app)

    policy = policy_factory("hybrid", hc)
    policy.validate()
    repo.add(policy)

    decision, _ = engine.run(app, policy)

    # mutate app AFTER decision
    app.applicant.credit_score = Decimal(300)
    repo.save(app)

    replayed, _ = engine.replay_decision(app.id, policy.id)

    assert not replayed.isequivalent(decision)


# =========================================================
# ENGINE RESPONDS TO APPLICATION CHANGES
# =========================================================

def test_engine_decision_changes_when_application_changes(loan_factory, policy_factory, clear_files):
    clear_files()

    hc = HashChain("tests/output/test_audit.jsonl")
    repo = Repository(hc)
    engine = DecisionEngine(hc, repo)

    app = loan_factory(hc)
    app.submit()
    app.validate()
    repo.add(app)

    policy = policy_factory("scorecard", hc)
    policy.validate()
    repo.add(policy)

    decision1, _ = engine.run(app, policy)

    # change application significantly
    app.requested_amount = Decimal("999999")
    app.validate()
    repo.save(app)

    decision2, _ = engine.run(app, policy)

    assert decision1.status != decision2.status


# =========================================================
# AUDIT EVENT CREATED
# =========================================================

def test_decision_creates_audit_event(loan_factory, policy_factory, clear_files):
    clear_files()

    hc = HashChain("tests/output/test_audit.jsonl")
    repo = Repository(hc)
    engine = DecisionEngine(hc, repo)

    app = loan_factory(hc)
    app.submit()
    app.validate()
    repo.add(app)

    policy = policy_factory("rulebased", hc)
    policy.validate()
    repo.add(policy)

    engine.run(app, policy)

    events = EmitEvent.events

    assert any(e.get("event") == "DECISIONED" for e in events)


# =========================================================
# AUDIT CHAIN VALIDATION
# =========================================================

def test_audit_chain_valid_after_engine_run(loan_factory, policy_factory, clear_files):
    clear_files()

    hc = HashChain("tests/output/test_audit.jsonl")
    repo = Repository(hc)
    engine = DecisionEngine(hc, repo)

    app = loan_factory(hc)
    app.submit()
    app.validate()
    repo.add(app)

    policy = policy_factory("hybrid", hc)
    policy.validate()
    repo.add(policy)

    engine.run(app, policy)

    valid, index = hc.verify_chain()

    assert valid
    assert index is None