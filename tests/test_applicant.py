from decimal import Decimal

from app.audit import HashChain, EmitEvent
from app.domain import Applicant
from app.persistence import JsonCrud


def test_applicant():
    hc = HashChain("tests/output/test_audit.jsonl")
    hc.clear()
    ee = EmitEvent("tests/output/test_events.jsonl")
    ee.clear()
    jc = JsonCrud("tests/output/test_events.jsonl")

    applicant = Applicant(
        "Alice",
        Decimal("80000"),
        Decimal("1500"),
        720,
        "EMPLOYED"
    )

    d = applicant.to_dict() 

    assert isinstance(d, dict) 
 
    j = applicant.to_json()

    a = Applicant.from_json(j) 

    assert a.name == "Alice"
    assert a.annual_income == Decimal("80000")
    assert a.monthly_debt == Decimal("1500")
    assert a.credit_score == 720 
    assert a.employment_status == "EMPLOYED"
    assert a.created_at == applicant.created_at

    a = Applicant.copy(applicant)
    assert a.name == "Alice"
    assert a.annual_income == Decimal("80000")
    assert a.monthly_debt == Decimal("1500")
    assert a.credit_score == 720
    assert a.employment_status == "EMPLOYED"
    assert a.created_at == applicant.created_at

    assert len(hc) == 0
    assert len(ee.events) == 1

