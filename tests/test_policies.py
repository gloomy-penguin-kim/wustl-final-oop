from __future__ import annotations

from app.audit import HashChain
from app.policies import RuleBasedPolicy, ScorecardPolicy, Policy, HybridPolicy
from app.repository.domain_repo import Repository
from app.rules import CreditScoreRule, DtiRule, EmploymentRule
from app.rules.loan_amount_rule import LoanAmountRule
import pytest



def test_policies(clear_files):
    hc, repo = clear_files()

    ru_policy = RuleBasedPolicy(hash_chain=hc,
                                id="testing_tacos_are_ruly_tacos",
                                rules=[EmploymentRule(), LoanAmountRule()])
    hy_policy = HybridPolicy(hash_chain=hc,
                             id="testing_tacos_are_hybrid_tacos",
                             rules=[CreditScoreRule(), DtiRule()])

    assert ru_policy.type == "RuleBasedPolicy"

    assert hy_policy.type == "HybridPolicy"

    hy_policy.validate()
    validated_at = hy_policy.validated_at
    hy_copy = hy_policy.copy()

    assert hy_policy.id == hy_copy.id
    assert hy_policy.type == hy_copy.type
    assert hy_policy.type == "HybridPolicy"
    assert hy_policy.policy == hy_copy.policy
    assert hy_policy.rules_as_strings == hy_copy.rules_as_strings
    assert hy_policy.created_at == hy_copy.created_at
    assert hy_policy.validated_at == validated_at
    assert hy_policy.validated_at == hy_copy.validated_at
    assert ru_policy.updated_at == ru_policy.updated_at

    j = ru_policy.to_json()
    assert ru_policy.id in j
    ru_policy2 = Policy.from_json(hc,j)
    assert ru_policy2.type == "RuleBasedPolicy"
    assert ru_policy2.rules_as_strings == ru_policy.rules_as_strings
    assert ru_policy2.created_at == ru_policy.created_at
    assert ru_policy2.validated_at == ru_policy.validated_at
    assert ru_policy2.updated_at == ru_policy.updated_at

    repo.save(ru_policy)
    ru_policy2 = repo.get(ru_policy.id)
    assert ru_policy2.type == "RuleBasedPolicy"
    assert ru_policy2.rules_as_strings == ru_policy.rules_as_strings
    assert ru_policy2.created_at == ru_policy.created_at
    assert ru_policy2.validated_at == ru_policy.validated_at
    assert ru_policy2.updated_at == ru_policy.updated_at



def test_policies_duplicates(clear_files):
    hc, repo = clear_files()

    sc_policy = ScorecardPolicy(id="testing_tacos_are_soft_tacos")
    sc_created_at = sc_policy.created_at
    repo.save(sc_policy)
    ru_policy = RuleBasedPolicy(id="testing_tacos_are_ruly_tacos", rules=[EmploymentRule(), LoanAmountRule()])
    repo.save(ru_policy)
    hy_policy = HybridPolicy(id="testing_tacos_are_hybrid_tacos", rules=[CreditScoreRule(), DtiRule()])
    repo.save(hy_policy)

    try: 
        sc_policy2 = ScorecardPolicy(id="testing_tacos_are_soft_tacos")
        assert sc_created_at == sc_policy.created_at
        repo.add(sc_policy2)
        raise AssertionError("should not allow duplicate id: ", sc_policy2.id)
    except Exception as e:
        pass 

def test_del_policy(clear_files):
    hc, repo = clear_files()

    sc_policy = ScorecardPolicy(hash_chain=hc,
                                id="testing_tacos_are_soft_tacos")
    repo.save(sc_policy)

    hy_policy = HybridPolicy(hash_chain=hc,
                             id="testing_tacos_are_hybrid_tacos",
                             rules=[CreditScoreRule(),
                                    DtiRule()])
    repo.save(hy_policy)

    new_sc_policy = repo.get("testing_tacos_are_soft_tacos")
    assert sc_policy.isequal(new_sc_policy)
    repo.delete(sc_policy.id)
    with pytest.raises(Exception):
        repo.get(sc_policy.id)

    ru_policy = RuleBasedPolicy(hash_chain=hc,
                                id="testing_tacos_are_soft_tacos",
                                rules=[EmploymentRule(),
                                       LoanAmountRule()])
    assert isinstance(ru_policy, RuleBasedPolicy)
    assert not ru_policy.isequal(new_sc_policy)
    assert 'EmploymentRule' in ru_policy.rules_as_strings
    assert 'LoanAmountRule' in ru_policy.rules_as_strings

def test_policy_update(clear_files):
    clear_files()

    hc = HashChain("tests/output/test_audit.jsonl")
    repo = Repository(hc,filename="tests/output/test_persistence.jsonl")

    hy_policy = HybridPolicy(hash_chain=hc,
                             id="testing_tacos_are_hybrid_tacos",
                             rules=[CreditScoreRule(),
                                    DtiRule()])
    hy_policy.id = "new testing taco id name"
    assert hy_policy.id == "new testing taco id name"

    hy_policy.rules = ['EmploymentRule']
    assert hy_policy.rules[0].__class__.__name__ == 'EmploymentRule'
    repo.save(hy_policy)
    hy_policy2 = repo.get(hy_policy.id, hash_chain=hc)
    assert hy_policy.id == hy_policy2.id
    assert hy_policy2.rules[0].__class__.__name__ == 'EmploymentRule'
