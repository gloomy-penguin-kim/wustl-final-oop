from datetime import datetime
from decimal import Decimal

import pytest

from app.audit import HashChain, EmitEvent
from app.domain import Applicant, LoanApplication
from app.domain.application import LoanAppInvalidIdError
from app.mixins.validate_base import ValidationError
from app.persistence import JsonCrud
from app.persistence.json_crud import DuplicateIDError



def test_applicant():
    hc = HashChain("tests/output/test_audit.jsonl")
    hc.clear()
    ee = EmitEvent("tests/output/test_events.jsonl")
    ee.clear()
    jc = JsonCrud("tests/output/test_persistence.jsonl")
    jc.clear()

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
        id="A1000",
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

    assert a.id == "A1000"
    assert a.requested_amount == Decimal("15000")
    assert a.term_months == 36
    assert a.purpose == "car"


def test_loans_crud():
    hc = HashChain("tests/output/test_audit.jsonl")
    hc.clear()
    ee = EmitEvent("tests/output/test_events.jsonl")
    ee.clear()
    jc = JsonCrud("tests/output/test_persistence.jsonl")
    jc.clear()

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

    try:
        app.submit()
        app.validate()
        raise AssertionError(f"not supposed to succeed.... {app.id}")
    except LoanAppInvalidIdError:
        pass

    app2 = LoanApplication(
        applicant={
            "name": "Bob",
            "annual_income": Decimal("15000"),
            "monthly_debt": Decimal("300"),
            "credit_score": 800,
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


def test_loans_duplicate():
    hc = HashChain("tests/output/test_audit.jsonl")
    hc.clear()
    ee = EmitEvent("tests/output/test_events.jsonl")
    ee.clear()
    jc = JsonCrud("tests/output/test_persistence.jsonl")
    jc.clear()

    with pytest.raises(Exception):
        _ = LoanApplication.load_from_file("something_really_specific")

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
        purpose="car",
        id="something_really_specific"
    )

    try:
        app2 = LoanApplication(
            applicant=Applicant(
                name="Alice",
                annual_income=Decimal("80000"),
                monthly_debt=Decimal("1500"),
                credit_score=720,
                employment_status="EMPLOYED"
            ),
            requested_amount=Decimal("15000"),
            term_months=36,
            purpose="car",
            id=app.id
        )
        raise AssertionError("1 - not supposed to pass, DuplicateIDError")

    except DuplicateIDError, ValidationError:
        pass

    app2 = LoanApplication(
        applicant=Applicant(
            name="Alice",
            annual_income=Decimal("80000"),
            monthly_debt=Decimal("1500"),
            credit_score=720,
            employment_status="EMPLOYED"
        ),
        requested_amount=Decimal("15000"),
        term_months=36,
        purpose="car",
        id="something_really_specific_else"
    )
    try:
        app2.id = app.id
        raise AssertionError("2 - not supposed to pass, DuplicateIDError")
    except DuplicateIDError:
        pass

    try:
        app2.id = "something_really_specific"
        raise AssertionError("3 - not supposed to pass, DuplicateIDError")
    except DuplicateIDError:
        pass


def test_loans_invalid():
    hc = HashChain("tests/output/test_audit.jsonl")
    hc.clear()
    ee = EmitEvent("tests/output/test_events.jsonl")
    ee.clear()
    jc = JsonCrud("tests/output/test_persistence.jsonl")
    jc.clear()

    try: 
        app = LoanApplication( 
            applicant=Applicant(
                name="Alice",
                annual_income=Decimal("80000"),
                monthly_debt=Decimal("1500"),
                credit_score=0,
                employment_status="EMPLOYED"
            ),
            requested_amount=Decimal("15000"),
            term_months=36,
            purpose="car"
        )
        raise AssertionError("1 - not supposed to pass, invalid value errors: ValidationError")
    except ValidationError as e:
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
        app.submit()
        app.validate()
        raise AssertionError("2 - not supposed to pass, invalid value errors: ValidationError")
    except ValidationError as e:
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
    app.submit()
    app.validate()

def test_loans_submit_validate():
    hc = HashChain("tests/output/test_audit.jsonl")
    hc.clear()
    ee = EmitEvent("tests/output/test_events.jsonl")
    ee.clear()
    jc = JsonCrud("tests/output/test_persistence.jsonl")
    jc.clear()
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
    app.submit()
    assert app.submitted_at is not None
    assert app.is_submitted
    app.validate()
    assert app.validated_at is not None
    assert app.is_validated

def test_loans_update():
    hc = HashChain("tests/output/test_audit.jsonl")
    hc.clear()
    ee = EmitEvent("tests/output/test_events.jsonl")
    ee.clear()
    jc = JsonCrud("tests/output/test_persistence.jsonl")
    jc.clear()
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
    app.applicant.name = "Alice 123"
    assert app.applicant.name == "Alice 123"
    app.save()
    b = LoanApplication.load_from_file(app.id)
    assert app.applicant.name == b.applicant.name == "Alice 123"
    app.submit()
    assert app.applicant.name == "Alice 123"
    b = LoanApplication.load_from_file(app.id)
    assert app.applicant.name == b.applicant.name == "Alice 123"
    assert app.submitted_at == b.submitted_at

    app.requested_amount = Decimal("15222")
    assert app.requested_amount == Decimal("15222")
    app.save()
    b = LoanApplication.load_from_file(app.id)
    assert app.requested_amount == b.requested_amount
    assert app.created_at == b.created_at


    app2 = LoanApplication(
        applicant=Applicant(
            name="Bob",
            annual_income=Decimal("22000"),
            monthly_debt=Decimal("300"),
            credit_score=725,
            employment_status="DISABLED"
        ),
        requested_amount=Decimal("10000"),
        term_months=72,
        purpose="car"
    )

    prev_id = app.id
    app.id = "something else"
    assert app.id == "something else"
    app.validate()
    assert app.id != prev_id
    assert app.id == "something else"
    app.save()
    b = LoanApplication.load_from_file("something else")
    assert app.id == b.id == "something else"
    with pytest.raises(Exception):
        app2.id = "something else"
    with pytest.raises(Exception):
        _ = LoanApplication.load_from_file(prev_id)



def test_loan_copy():
    hc = HashChain("tests/output/test_audit.jsonl")
    hc.clear()
    ee = EmitEvent("tests/output/test_events.jsonl")
    ee.clear()
    jc = JsonCrud("tests/output/test_persistence.jsonl")
    jc.clear()
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
    app.submit()

    app2 = app.copy()
    assert app2.created_at == app.created_at
    assert app2.submitted_at == app.submitted_at
    assert app2.isequal(app)