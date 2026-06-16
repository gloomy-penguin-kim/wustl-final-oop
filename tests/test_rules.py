from collections import defaultdict

import pytest
from decimal import Decimal

from app.rules import EmploymentRule, DtiRule, CreditScoreRule, RuleStatus
from app.rules.loan_amount_rule import LoanAmountRule


# =========================================================
# EMPLOYMENT RULE
# =========================================================

def test_employment_rule_passes_for_employed(loan_factory):
    app = loan_factory()
    rule = EmploymentRule()

    ctx = defaultdict(dict)
    result = rule.apply(app, ctx)

    assert result.status == RuleStatus.APPROVE


def test_employment_rule_fails_for_unemployed(loan_factory):
    app = loan_factory()
    app.applicant.employment_status = "UNEMPLOYED"
    app.requested_amount = Decimal("45000")

    rule = EmploymentRule()

    ctx = defaultdict(dict)
    result = rule.apply(app, ctx)

    assert result.status == RuleStatus.DECLINE


# =========================================================
# CREDIT SCORE RULE
# =========================================================

def test_credit_score_rule_passes_high_score(loan_factory):
    app = loan_factory()
    app.applicant.credit_score = 750

    rule = CreditScoreRule()

    ctx = defaultdict(dict)
    result = rule.apply(app, ctx)

    assert result.status != RuleStatus.DECLINE


def test_credit_score_rule_fails_low_score(loan_factory):
    app = loan_factory()
    app.applicant.credit_score = 400

    rule = CreditScoreRule()

    ctx = defaultdict(dict)
    result = rule.apply(app, ctx)

    assert result.status == RuleStatus.DECLINE


def test_credit_score_rule_boundary(loan_factory):
    app = loan_factory()
    app.applicant.credit_score = 600  # adjust to your threshold

    rule = CreditScoreRule()

    ctx = defaultdict(dict)
    result = rule.apply(app, ctx)

    # Don't assume pass/fail — just ensure it returns something valid
    assert result.status == RuleStatus.REFER


# =========================================================
# DTI RULE (Debt-to-Income)
# =========================================================

def test_dti_rule_passes_low_dti(loan_factory):
    app = loan_factory()
    app.applicant.monthly_debt = Decimal("500")
    app.applicant.annual_income = Decimal("100000")

    rule = DtiRule()

    ctx = defaultdict(dict)
    result = rule.apply(app, ctx)

    assert result.status != RuleStatus.DECLINE


def test_dti_rule_fails_high_dti(loan_factory):
    app = loan_factory()
    app.applicant.monthly_debt = Decimal("5000")
    app.applicant.annual_income = Decimal("20000")

    rule = DtiRule()

    ctx = defaultdict(dict)
    result = rule.apply(app, ctx)

    assert result.status == RuleStatus.DECLINE


# =========================================================
# LOAN AMOUNT RULE
# =========================================================

def test_loan_amount_rule_passes_reasonable_amount(loan_factory):
    app = loan_factory()
    app.requested_amount = Decimal("15000")

    rule = LoanAmountRule()

    ctx = defaultdict(dict)
    result = rule.apply(app, ctx)

    assert result.status != RuleStatus.DECLINE


def test_loan_amount_rule_fails_excessive_amount(loan_factory):
    app = loan_factory()
    app.requested_amount = Decimal("999999")

    rule = LoanAmountRule()

    ctx = defaultdict(dict)
    result = rule.apply(app, ctx)

    assert result.status == RuleStatus.DECLINE


# =========================================================
# RULE CONSISTENCY (NO EXCEPTIONS)
# =========================================================

@pytest.mark.parametrize("rule_cls", [
    EmploymentRule,
    DtiRule,
    CreditScoreRule,
    LoanAmountRule
])
def test_all_rules_return_valid_result(rule_cls, loan_factory):
    app = loan_factory()
    rule = rule_cls()

    ctx = defaultdict(dict)
    result = rule.apply(app, ctx)

    assert result is not None
    assert hasattr(result, "status")
    assert result.status in {
        RuleStatus.APPROVE,
        RuleStatus.DECLINE,
        RuleStatus.REFER
    }