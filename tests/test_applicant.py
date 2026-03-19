from decimal import Decimal

import pytest

from app.domain import Applicant

def test_applicant(): 
     
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
