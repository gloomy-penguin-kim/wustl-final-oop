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
    jc.clear()

    applicant = Applicant(
        name="Alice",
        annual_income=Decimal("80000"),
        monthly_debt=Decimal("1500"),
        credit_score=720,
        employment_status="EMPLOYED"
    )

    d = applicant.to_dict() 

    assert isinstance(d, dict) 
 
    j = applicant.to_json()

    assert isinstance(j, str)

    a = Applicant.from_json(j)

    assert isinstance(a, Applicant)

    assert a.name == "Alice"
    assert a.annual_income == Decimal("80000")
    assert a.monthly_debt == Decimal("1500")
    assert a.credit_score == 720 
    assert a.employment_status == "EMPLOYED"
    assert a.created_at == applicant.created_at

    a = applicant.copy()
    assert a.name == "Alice"
    assert a.annual_income == Decimal("80000")
    assert a.monthly_debt == Decimal("1500")
    assert a.credit_score == 720
    assert a.employment_status == "EMPLOYED"
    assert a.created_at == applicant.created_at
    assert a.updated_at == applicant.updated_at
    assert a.validated_at == applicant.validated_at
