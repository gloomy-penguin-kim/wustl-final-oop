from datetime import datetime
from decimal import ROUND_HALF_UP, Decimal

import pytest

from app.domain.applicant import Applicant
from app.domain.application import LoanApplication
from app.engine.decision_engine import DecisionEngine
from app.policies.rule_based_policy import RuleBasedPolicy
from app.rules.credit_score_rule import CreditScoreRule
from app.rules.dti_rule import DtiRule
from app.rules.employment_rule import EmploymentRule
from app.rules.loan_amount_rule import LoanAmountRule
from app.rules.rule_result import Status
from app.wrappers.loans import Loans
from app.wrappers.policies import Policies

 
 
def test_rules_credit_score_rule(): 
         
    app = LoanApplication( 
        Applicant(
            "Alice",
            Decimal("80000"),
            Decimal("1500"),
            500,
            "EMPLOYED"
        ) ,
        Decimal("15000"),
        36,
        "car" 
    )

    loans = Loans("test_loans.jsonl")
    loans.register(app)

    policies = Policies("test_policies.jsonl")
    policies.delete("just_credit_score")

    policies.register(RuleBasedPolicy("just_credit_score", [CreditScoreRule()]))
    
    decision = DecisionEngine(loans, policies)
    d, c = decision.run(app, "just_credit_score")

    assert d.status == Status.DECLINE 
    assert d.reason_codes[0] == "CS100"
    assert len(d.reason_codes) == 1 
    assert "CS100" in c 
    assert c["CS100"] == 'low credit score < 550'  


def test_employment_rule(): 
         
    app = LoanApplication( 
        Applicant(
            "Alice",
            Decimal("80000"),
            Decimal("3000"),
            500,
            "EMPLOYED"
        ) ,
        Decimal("15000"),
        36,
        "car" 
    )

    assert app.applicant.dti() == Decimal(0.45).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    loans = Loans("test_loans.jsonl")
    loans.register(app)

    policies = Policies("test_policies.jsonl")
    policies.delete("test_just_dti")

    policies.register(RuleBasedPolicy("test_just_dti", [DtiRule()]))
    
    decision = DecisionEngine(loans, policies)
    d, c = decision.run(app, "test_just_dti") 

    assert d.status == Status.REFER 
    assert d.reason_codes[0] == "DIT30"
    assert len(d.reason_codes) == 1 
    assert "DIT30" in c 
    assert c["DIT30"] == "DTI is above 0.43"  
 

def test_debt_to_income(): 
         
    app = LoanApplication( 
        Applicant(
            "Alice",
            Decimal("80000"),
            Decimal("3000"),
            500,
            "EMPLOYED"
        ) ,
        Decimal("15000"),
        36,
        "car" 
    )

    assert app.applicant.dti() == Decimal(0.45).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    loans = Loans("test_loans.jsonl")
    loans.register(app)

    policies = Policies("test_policies.jsonl")
    policies.delete("test_just_dti")

    policies.register(RuleBasedPolicy("test_just_dti", [DtiRule()]))
    
    decision = DecisionEngine(loans, policies)
    d, c = decision.run(app, "test_just_dti") 

    assert d.status == Status.REFER 
    assert d.reason_codes[0] == "DIT30"
    assert len(d.reason_codes) == 1 
    assert "DIT30" in c 
    assert c["DIT30"] == "DTI is above 0.43"  
 
 
def test_employment_status_vs_income(): 
         
    app = LoanApplication( 
        Applicant(
            "Alice",
            Decimal("45000"),
            Decimal("3000"),
            500,
            "UNEMPLOYED",
            True
        ) ,
        Decimal("15000"),
        36,
        "car" 
    ) 

    assert app.requested_amount_vs_term_months_vs_income().quantize(Decimal("0.01"), rounding=ROUND_HALF_UP) == Decimal(0.11).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    loans = Loans("test_loans.jsonl")
    loans.register(app)

    policies = Policies("test_policies.jsonl")
    policies.delete("test_just_employment")

    policies.register(RuleBasedPolicy("test_just_employment", [EmploymentRule()]))
    
    decision = DecisionEngine(loans, policies)
    d, c = decision.run(app, "test_just_employment")  

    assert d.status == Status.REFER 
    assert d.reason_codes[0] == "EM333"
    assert len(d.reason_codes) == 1 
    assert "EM333" in c 
    assert c["EM333"] == "no employment, but existing customer and high enough income"
 
 
def test_loan_amount(): 
         
    app = LoanApplication( 
        Applicant(
            "Alice",
            Decimal("45000"),
            Decimal("3000"),
            500,
            "UNEMPLOYED",
            True
        ) ,
        Decimal("15000"),
        36,
        "car" 
    )  
    assert app.applicant.income_vs_monthly_debt().quantize(Decimal("0.01"), rounding=ROUND_HALF_UP) == Decimal(750).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    loans = Loans("test_loans.jsonl")
    loans.register(app)

    policies = Policies("test_policies.jsonl")
    policies.delete("test_just_loan_amount")

    policies.register(RuleBasedPolicy("test_just_loan_amount", [LoanAmountRule()]))
    
    decision = DecisionEngine(loans, policies)
    d, c = decision.run(app, "test_just_loan_amount")  
  
    assert d.status == Status.DECLINE 
    assert d.reason_codes[0] == "LA500"
    assert len(d.reason_codes) == 1 
    assert "LA500" in c 
    assert c["LA500"] == "monthly disposable income vs monthly payment"

 