from datetime import datetime
from decimal import Decimal

import pytest

from app.audit import HashChain, EmitEvent
from app.domain import Applicant, LoanApplication
from app.mixins.validate_base import ValidationError
from app.persistence import JsonCrud
from app.repository.domain_repo import Repository



def test_applicant(clear_files):
    hc, repo = clear_files()

    applicant = Applicant(
            name="Alice",
            annual_income=Decimal("80000"),
            monthly_debt=Decimal("1500"),
            credit_score=720,
            employment_status="EMPLOYED",
            hash_chain=hc,
        )

    app = LoanApplication( 
        applicant=applicant,
        requested_amount=Decimal("15000"),
        term_months=36,
        purpose="car",
        id="A1000",
        hash_chain=hc,
    )

    d = app.to_dict() 

    assert isinstance(d, dict) 
    
    j = app.to_json() 
    a = LoanApplication.from_json(hc, j)

    assert a.applicant.name == "Alice"
    assert a.applicant.annual_income == Decimal("80000")
    assert a.applicant.monthly_debt == Decimal("1500")
    assert a.applicant.credit_score == 720 
    assert a.applicant.employment_status == "EMPLOYED"

    assert a.id == "A1000"
    assert a.requested_amount == Decimal("15000")
    assert a.term_months == 36
    assert a.purpose == "car"


def test_loans_crud(clear_files):
    hc, repo = clear_files()

    applicant = Applicant(
        "Alice",
        Decimal("80000"),
        Decimal("1500"),
        720,
        "EMPLOYED",
        hash_chain=hc,
    )
    assert applicant.hash_chain == hc
    repo.save(applicant)
    applicant2 = repo.get(applicant.id)
    assert applicant.isequal(applicant2)

    repo.delete("tacobell")

    app = LoanApplication(
        applicant=applicant,
        requested_amount=Decimal("15000"),
        term_months=36,
        purpose="car",
        id="tacobell",
        hash_chain=hc,
    )
    print("APPPPPPPPPPP", app.hash_chain)

    app_copy = app.copy()
    assert app.requested_amount == app_copy.requested_amount
    assert app.created_at == app_copy.created_at
    assert app.submitted_at == app_copy.submitted_at
    assert app.validated_at == app_copy.validated_at
    assert app.applicant.name == app_copy.applicant.name
    assert app.applicant.isequal(app_copy.applicant)

    repo = Repository(hash_chain=hc,filename="tests/output/test_persistence.jsonl")
    print("APPPPPPPPPPP11111", app.hash_chain)
    repo.save(app)
    print("APPPPPPPPPPP22222222", app.hash_chain)
    app2 = repo.get(app.id, hash_chain=hc)
    print("APPPPPPPPPPP33333333", app.hash_chain)
    print("APPPPPPPPPPP22222", app2.hash_chain)

    assert app2.requested_amount == app_copy.requested_amount
    assert app2.created_at == app_copy.created_at
    assert app2.submitted_at == app_copy.submitted_at
    assert app2.validated_at == app_copy.validated_at
    assert app2.applicant.name == app_copy.applicant.name
    assert app2.applicant.isequal(app_copy.applicant)

    repo.delete(app)

    try:
        app.submit()
        app.validate()
        repo.save(app)
        raise AssertionError(f"not supposed to succeed.... {app.id}")
    except Exception:
        pass

    app2 = LoanApplication(
        applicant={
            "name": "Bob",
            "annual_income": Decimal("15000"),
            "monthly_debt": Decimal("300"),
            "credit_score": 800,
            "employment_status": "SOCIAL SECURITY",
            "hash_chain": hc,
        },
        requested_amount=Decimal("15000"),
        term_months=36,
        purpose="car",
        id="tacobell",
        hash_chain=hc,
    )

    app2.submit()
    app_copy = app2.copy()
    app2.validate()

    assert app2.requested_amount == app_copy.requested_amount
    assert app2.created_at == app_copy.created_at
    assert app2.submitted_at == app_copy.submitted_at
    assert app2.validated_at != app_copy.validated_at
    assert app2.applicant.name == app_copy.applicant.name
    assert app2.applicant.created_at == app_copy.applicant.created_at


def test_loans_duplicate(clear_files, loan_factory):
    clear_files()
    hc = HashChain("tests/output/test_audit.jsonl")
    repo = Repository(hc, filename="tests/output/test_persistence.jsonl")

    with pytest.raises(Exception):
        _ = repo.get("something_really_specific")

    app = loan_factory(hc)

    try:
        app2 = loan_factory(hc)
        app2.id = app.id
        repo.save(app2)
        raise AssertionError("1 - not supposed to pass, DuplicateIDError")

    except Exception:
        pass



def test_loans_invalid(clear_files, loan_factory):
    clear_files()
    hc = HashChain("tests/output/test_audit.jsonl")

    try:
        app = loan_factory(hc)
        app.applicant.credit_score = 299
        app.submit()
        app.validate()
        raise AssertionError("1 - not supposed to pass, invalid value errors: ValidationError")
    except ValidationError as e:
        assert str(e) == "Invalid credit score" 

    try:
        app = loan_factory(hc)
        app.requested_amount = -15000
        app.submit()
        app.validate()
        raise AssertionError("2 - not supposed to pass, invalid value errors: ValidationError")
    except ValidationError as e:
        assert str(e) == "Invalid loan amount" 
 
    app = loan_factory(hc)
    app.submit()
    app.validate()

def test_loans_submit_validate(clear_files, loan_factory):
    clear_files()
    hc = HashChain("tests/output/test_audit.jsonl")
    app = loan_factory(hc)
    app.submit()
    assert app.submitted_at is not None
    assert app.is_submitted
    app.validate()
    assert app.validated_at is not None
    assert app.is_validated

def test_loans_update(clear_files, loan_factory):
    clear_files()
    hc = HashChain("tests/output/test_audit.jsonl")
    app = loan_factory(hc)
    repo = Repository(hc, "tests/output/test_persistence.jsonl")
    app.applicant.name = "Alice 123"
    assert app.applicant.name == "Alice 123"
    repo.save(app)
    b = repo.get(app.id)
    assert app.applicant.name == b.applicant.name == "Alice 123"
    app.submit()
    repo.save(app)
    assert app.applicant.name == "Alice 123"
    b = repo.get(app.id)
    assert app.applicant.name == b.applicant.name == "Alice 123"
    assert app.submitted_at == b.submitted_at

    app.requested_amount = Decimal("15222")
    assert app.requested_amount == Decimal("15222")
    repo.save(app)
    b = repo.get(app.id)
    assert app.requested_amount == b.requested_amount
    assert app.created_at == b.created_at

    prev_id = app.id
    app.id = "something else"
    assert app.id == "something else"
    app.validate()
    assert app.id != prev_id
    assert app.id == "something else"
    repo.save(app)
    b = repo.get(app.id)
    assert app.id == b.id == "something else"
    assert repo.existing(app.id)
    repo.delete(app)
    with pytest.raises(Exception):
        repo.get(app.id)




def test_loan_copy(clear_files, loan_factory):
    clear_files()
    hc = HashChain("tests/output/test_audit.jsonl")
    app = loan_factory(hc)
    app2 = app.copy()
    assert app2.created_at == app.created_at
    assert app2.submitted_at == app.submitted_at
    assert app2.isequal(app)