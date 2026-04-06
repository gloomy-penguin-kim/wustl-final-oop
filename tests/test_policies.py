from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from app.audit import HashChain, EmitEvent
from app.persistence import JsonCrud, DuplicateIDError
from app.policies import RuleBasedPolicy, ScorecardPolicy, Policy, HybridPolicy
from app.rules import CreditScoreRule, DtiRule, EmploymentRule
from app.rules.loan_amount_rule import LoanAmountRule
import pytest




def test_policies():
    hc = HashChain("tests/output/test_audit.jsonl")
    hc.clear()
    ee = EmitEvent("tests/output/test_events.jsonl")
    ee.clear()
    jc = JsonCrud("tests/output/test_persistence.jsonl")
    jc.clear()

    ru_policy = RuleBasedPolicy(id="testing_tacos_are_ruly_tacos", rules=[EmploymentRule(), LoanAmountRule()])
    hy_policy = HybridPolicy(id="testing_tacos_are_hybrid_tacos", rules=[CreditScoreRule(), DtiRule()])

    assert ru_policy.type == "Policy"
    assert ru_policy.policy == "RuleBasedPolicy"

    assert hy_policy.type == "Policy"
    assert hy_policy.policy == "HybridPolicy"

    hy_policy.validate()
    validated_at = hy_policy.validated_at
    hy_copy = hy_policy.copy()
    print(hy_policy.validated_at)
    print(hy_copy.validated_at)

    assert hy_policy.id == hy_copy.id
    assert hy_policy.type == hy_copy.type
    assert hy_policy.type == "Policy"
    assert hy_policy.policy == hy_copy.policy
    assert hy_policy.policy == "HybridPolicy"
    assert hy_policy.rules_as_strings == hy_copy.rules_as_strings
    assert hy_policy.created_at == hy_copy.created_at
    assert hy_policy.validated_at == validated_at
    assert hy_policy.validated_at == hy_copy.validated_at
    assert ru_policy.updated_at == ru_policy.updated_at

    j = ru_policy.to_json()
    assert ru_policy.id in j
    ru_policy2 = Policy.from_json(j)
    assert ru_policy2.type == "Policy"
    assert ru_policy2.policy == "RuleBasedPolicy"
    assert ru_policy2.rules_as_strings == ru_policy.rules_as_strings
    assert ru_policy2.created_at == ru_policy.created_at
    assert ru_policy2.validated_at == ru_policy.validated_at
    assert ru_policy2.updated_at == ru_policy.updated_at


def test_policies_duplicates():
    hc = HashChain("tests/output/test_audit.jsonl")
    hc.clear()
    ee = EmitEvent("tests/output/test_events.jsonl")
    ee.clear()
    jc = JsonCrud("tests/output/test_persistence.jsonl")
    jc.clear()

    sc_policy = ScorecardPolicy(id="testing_tacos_are_soft_tacos")
    sc_created_at = sc_policy.created_at
    ru_policy = RuleBasedPolicy(id="testing_tacos_are_ruly_tacos", rules=[EmploymentRule(), LoanAmountRule()])
    hy_policy = HybridPolicy(id="testing_tacos_are_hybrid_tacos", rules=[CreditScoreRule(), DtiRule()])

    try: 
        sc_policy2 = ScorecardPolicy(id="testing_tacos_are_soft_tacos")
        assert sc_created_at == sc_policy.created_at
        raise AssertionError("should not allow duplicate id: ", sc_policy2.id)
    except DuplicateIDError as e:
        pass 

    try:
        ru_policy.id = sc_policy.id
        assert sc_created_at == sc_policy.created_at
        raise AssertionError("should not allow duplicate id: ", sc_policy.id)
    except DuplicateIDError as e:
        pass

def test_del_policy():
    hc = HashChain("tests/output/test_audit.jsonl")
    hc.clear()
    ee = EmitEvent("tests/output/test_events.jsonl")
    ee.clear()
    jc = JsonCrud("tests/output/test_persistence.jsonl")
    jc.clear()

    sc_policy = ScorecardPolicy(id="testing_tacos_are_soft_tacos")
    hy_policy = HybridPolicy(id="testing_tacos_are_hybrid_tacos", rules=[CreditScoreRule(), DtiRule()])

    new_sc_policy = Policy.load_from_file("testing_tacos_are_soft_tacos")
    assert sc_policy.isequal(new_sc_policy)
    Policy.delete(sc_policy.id)
    with pytest.raises(Exception):
        _ = Policy.load_from_file("testing_tacos_are_soft_tacos")

    ru_policy = RuleBasedPolicy(id="testing_tacos_are_soft_tacos", rules=[EmploymentRule(), LoanAmountRule()])
    assert isinstance(ru_policy, RuleBasedPolicy)
    assert not ru_policy.isequal(new_sc_policy)
    assert 'EmploymentRule' in ru_policy.rules_as_strings
    assert 'LoanAmountRule' in ru_policy.rules_as_strings

def test_policy_update():
    hc = HashChain("tests/output/test_audit.jsonl")
    hc.clear()
    ee = EmitEvent("tests/output/test_events.jsonl")
    ee.clear()
    jc = JsonCrud("tests/output/test_persistence.jsonl")
    jc.clear()

    hy_policy = HybridPolicy(id="testing_tacos_are_hybrid_tacos", rules=[CreditScoreRule(), DtiRule()])
    hy_policy.id = "new testing taco id name"
    assert hy_policy.id == "new testing taco id name"

    hy_policy.rules = ['EmploymentRule']
    assert hy_policy.rules[0].__class__.__name__ == 'EmploymentRule'
    hy_policy.save()
    hy_policy2 = Policy.load_from_file(hy_policy.id)
    assert hy_policy.id == hy_policy2.id
    assert hy_policy2.rules[0].__class__.__name__ == 'EmploymentRule'
