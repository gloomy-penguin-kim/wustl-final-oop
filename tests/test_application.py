from datetime import datetime
from decimal import Decimal

import pytest

from app.domain import Applicant, LoanApplication
from app.engine import Loans
from app.settings import Config

Config.AUDIT_FILE = "tests/output/emit_events.jsonl"


def test_applicant(): 
        
    applicant = Applicant(
            "Alice",
            Decimal("80000"),
            Decimal("1500"),
            720,
            "EMPLOYED"
        )

    app = LoanApplication( 
        applicant,
        Decimal("15000"),
        36,
        "car",
        application_id="A1000"
    )

    d = app.to_dict() 

    assert isinstance(d, dict) 
    
    j = app.to_json() 
    a = LoanApplication.from_json(j) 

    assert a.applicant.name == "Alice"
    assert a.applicant.annual_income == Decimal("80000")
    assert a.applicant.monthly_debt == Decimal("1500")
    assert a.applicant.credit_score == 720 
    assert a.applicant.employment_status == "EMPLOYED"

    assert a.application_id == "A1000"
    assert a.requested_amount == Decimal("15000")
    assert a.term_months == 36
    assert a.purpose == "car"


def test_loans():     
    loans = Loans("tests/output/test_loans.jsonl")
    loans.clear() 

    applicant = Applicant(
            name="Alice",
            annual_income=Decimal("80000"),
            monthly_debt=Decimal("1500"),
            credit_score=720,
            employment_status="EMPLOYED"
        )
    
    app = LoanApplication( 
        applicant=applicant,
        requested_amount=Decimal("15000"),
        term_months=36,
        purpose="car"
    )

    loans.register(app)  
    assert app.application_id in loans.items 
    
    app2 = loans.new( 
        applicant=applicant,
        requested_amount=Decimal("15000"),
        term_months=36,
        purpose="car"
    )

    assert isinstance(app2, LoanApplication)
    assert app2.application_id in loans.items 
    
    app3 = loans.new({
        "applicant": applicant,
        "requested_amount": Decimal("15000"),
        "term_months":36,
        "purpose": "car" 
        })

    assert isinstance(app3, LoanApplication)
    assert app3.application_id in loans.items 
    
    app4 = loans.new({     
        "applicant": { "name": "bob", 
                      "annual_income": Decimal(100000), 
                      "monthly_debt": Decimal(2500), 
                      "credit_score": 820, 
                      "employment_status": "EMPLOYED" },
        "requested_amount": Decimal("15000"),
        "term_months":36,
        "purpose": "car",
        "application_id": "custom_id_1234"
        })

    assert isinstance(app4, LoanApplication)
    assert isinstance(app4.applicant, Applicant)
    assert app4.application_id in loans.items 
    assert "custom_id_1234" in loans.items 
     
    loans.delete(app.application_id)
    assert app.application_id not in loans.items 
    assert app2.application_id in loans.items 
    assert app3.application_id in loans.items   
    assert app4.application_id in loans.items

    loans.delete(app2.application_id)
    assert app3.application_id in loans.items   
    assert app4.application_id in loans.items 

    loans.delete(app3.application_id)
    assert app4.application_id in loans.items 

    loans.delete(app4.application_id)
    assert app4.application_id not in loans.items 


def test_loans_duplicate(): 
    loans = Loans("tests/output/test_loans.jsonl")
    loans.clear() 

    applicant = Applicant(
            name="Alice",
            annual_income=Decimal("80000"),
            monthly_debt=Decimal("1500"),
            credit_score=720,
            employment_status="EMPLOYED"
        )
    
    app = LoanApplication( 
        applicant=applicant,
        requested_amount=Decimal("15000"),
        term_months=36,
        purpose="car",
        application_id="duplicate_id_1234"
    )

    loans.register(app)  
    assert app.application_id in loans.items 

    with pytest.raises(ValueError): 
        loans.register(app)

    loans.clear() 


def test_loans_invalid(): 
    loans = Loans("tests/output/test_loans.jsonl")
    loans.clear() 

    try: 
        app = LoanApplication( 
            applicant=Applicant(
                name="Alice",
                annual_income=Decimal("80000"),
                monthly_debt=Decimal("1500"),
                credit_score=720,
                employment_status="EMPLOYED"
            ),
            requested_amount=Decimal("15000"),
            term_months=36,
            purpose="car"
        )
    except ValueError as e:
        assert str(e) == "Invalid credit score" 

    try:
        app = LoanApplication( 
            applicant=Applicant(
                name="Alice",
                annual_income=Decimal("80000"),
                monthly_debt=Decimal("1500"),
                credit_score=700,
                employment_status="EMPLOYED"
            ),
            requested_amount=Decimal("-15000"),
            term_months=36,
            purpose="car" 
        )
    except ValueError as e:
        assert str(e) == "Invalid loan amount" 
 
    app = LoanApplication( 
        applicant=Applicant(
            name="Alice",
            annual_income=Decimal("0"),
            monthly_debt=Decimal("1500"),
            credit_score=700,
            employment_status="EMPLOYED"
        ),
        requested_amount=Decimal("15000"),
        term_months=36,
        purpose="car"
    )


    loans.clear()


def test_loans_to_json():
    loans = Loans("tests/output/test_loans.jsonl")
    loans.clear()

    app = LoanApplication(
        applicant=Applicant(
            name="Alice",
            annual_income=Decimal("0"),
            monthly_debt=Decimal("1500"),
            credit_score=700,
            employment_status="EMPLOYED"
        ),
        requested_amount=Decimal("15000"),
        term_months=36,
        purpose="car",
        application_id="testing_tacos_are_soft_tacos"
    )

    j = app.to_json()
    assert "testing_tacos_are_soft_tacos" in j
    l = LoanApplication.from_json(j)
    assert "testing_tacos_are_soft_tacos" == l.application_id
    assert app.submitted_at == l.submitted_at

    loans.clear()