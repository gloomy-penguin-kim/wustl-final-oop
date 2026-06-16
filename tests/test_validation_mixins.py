import pytest
from decimal import Decimal

from app.domain import Applicant
from app.mixins.validate_base import ValidationError


# =========================================================
# VALID CASE (BASELINE)
# =========================================================

def test_valid_application_passes_validation(loan_factory):
    app = loan_factory()
    app.submit()

    # should not raise
    app.validate()


# =========================================================
# LOAN APPLICATION VALIDATION FAILURES
# =========================================================

def test_invalid_loan_amount_raises(loan_factory):
    app = loan_factory()
    app.requested_amount = Decimal("0")
    app.submit()

    with pytest.raises(ValidationError):
        app.validate()


def test_invalid_term_raises(loan_factory):
    app = loan_factory()
    app.term_months = 13  # not allowed
    app.submit()

    with pytest.raises(ValidationError):
        app.validate()


def test_missing_purpose_raises(loan_factory):
    app = loan_factory()
    app.purpose = ""
    app.submit()

    with pytest.raises(ValidationError):
        app.validate()


def test_missing_created_at_raises(loan_factory):
    app = loan_factory()
    app.created_at = None
    app.submit()

    with pytest.raises(ValidationError):
        app.validate()


def test_missing_submitted_at_raises(loan_factory):
    app = loan_factory()
    # simulate not submitted
    app.submitted_at = None

    with pytest.raises(ValueError):
        app.validate()



# =========================================================
# APPLICANT VALIDATION TESTS
# =========================================================

def test_valid_applicant_passes():
    applicant = Applicant(
        name="Alice",
        annual_income=Decimal("50000"),
        monthly_debt=Decimal("1000"),
        credit_score=700,
        employment_status="EMPLOYED",
    )

    # assuming Applicant has validate()
    applicant.validate()


def test_invalid_credit_score_raises():
    with pytest.raises(ValidationError):
        applicant = Applicant(
            name="Alice",
            annual_income=Decimal("50000"),
            monthly_debt=Decimal("1000"),
            credit_score=-10,  # invalid
            employment_status="EMPLOYED",
        )



def test_invalid_income_raises():
    with pytest.raises(ValidationError):
        applicant = Applicant(
            name="Alice",
            annual_income=Decimal("-1"),
            monthly_debt=Decimal("1000"),
            credit_score=700,
            employment_status="EMPLOYED",
        )


# =========================================================
# SUPER() CHAIN TEST (VERY IMPORTANT)
# =========================================================

def test_validation_chain_runs_all_mixins(loan_factory):
    """
    This ensures that super().validate() is being called properly
    across mixins.
    """
    app = loan_factory()
    app.submit()

    app.applicant.credit_score = -1

    with pytest.raises(ValidationError):
        app.validate()