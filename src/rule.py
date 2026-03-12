
from abc import ABC, abstractmethod
from dataclasses import dataclass
from decimal import Decimal

from models import Loan, Status


LOW = Decimal(0.09)
MEDIUM = Decimal(0.16)
HIGH = Decimal(0.22)

@dataclass 
class RuleResult: 
    status: Status  | None = None 
    code: str       | None = None 
    apr:  Decimal   | None = None 

    
class Rule(ABC): 
    @abstractmethod
    def apply(self, loan: Loan, ctx: dict) -> RuleResult:...  

class Rule_DTI_Lte_30(Rule): 
    def __init__(self): 
        self.code = "DIT30" 
        self.reason = "DTI is below 30"
    def apply(self, loan: Loan, ctx: dict) -> RuleResult: 
        dti = loan.applicant.debt_to_income_ratio() 
        if (dti and dti <= 30): 
            ctx[Status.APPROVE].append(self.code)
            return RuleResult(apr=LOW, status=Status.APPROVE, code=self.code)
        return RuleResult()  
 
# class Rule_Credit_Score_Gte_775(Rule): 
#     def __init__(self): 
#         self.code = "CS775" 
#         self.reason = "credit score is above 800"
#     def apply(self, loan: Loan, ctx: dict) -> RuleResult:
#         if loan.applicant.credit_score and loan.applicant.credit_score >= 800: 
#             ctx[Status.APPROVE].append(code=self.code)
#             return RuleResult(apr=LOW, status=Status.APPROVE, code=self.code)
#         return RuleResult()  

# class Rule_DTI_Gte_50(Rule): 
#     def __init__(self): 
#         self.code = "DT050" 
#         self.reason = "DTI is high"
#     def apply(self, loan: Loan, ctx: dict) -> RuleResult:
#         if (loan.applicant.debt_to_income_ratio() >= 50): 
#             ctx[Status.DECLINE].append(self.code)
#             return RuleResult(status=Status.DECLINE, code=self.code) 
#         elif (loan.applicant.debt_to_income_ratio() > 47): 
#             ctx[Status.REFER].append(self.code)
#             return RuleResult(apr=HIGH, status=Status.REFER, code=self.code)
#         return RuleResult()  
 
# class Rule_Annual_Income(Rule): 
#     def __init__(self): 
#         self.code = "AI200" 
#         self.reason = "annual income must exceed requested amount" 
#     def apply(self, loan: Loan, ctx: dict) -> RuleResult:
#         if loan.applicant.annual_income and loan.requested_amount and loan.term_months and loan.applicant.monthly_debt: 
#             if (loan.applicant.annual_income >= (loan.requested_amount/loan.term_months)*12*3): 
#                 ctx[Status.APPROVE].append(self.code)
#                 return RuleResult(apr=LOW, status=Status.APPROVE, code=self.code)
#             elif (loan.applicant.annual_income-Decimal(loan.applicant.monthly_debt*12) >= (loan.requested_amount/loan.term_months)*12): 
#                 ctx[Status.REFER].append(self.code)
#                 return RuleResult(apr=MEDIUM, status=Status.REFER, code=self.code)
#             else: 
#                 ctx[Status.DECLINE].append(self.code)
#                 return RuleResult(status=Status.DECLINE, code=self.code)  
#         return RuleResult() 

# class Rule_DTI_Lte_43_and_Credit_Score_Gte_715_and_Employeed(Rule): 
#     def __init__(self): 
#         self.code = "DT143" 
#         self.reason = "DTI <= 43, credit score >= 715 and employed"
#     def apply(self, loan: Loan, ctx: dict) -> RuleResult:
#         if ((loan.applicant.debt_to_income_ratio() <= 43) and 
#             (loan.applicant.credit_score and loan.applicant.credit_score >= 715)):
#             if (loan.applicant.employment_status and loan.applicant.employment_status): 
#                 ctx[Status.APPROVE].append(self.code)
#                 return RuleResult(apr=MEDIUM, status=Status.APPROVE, code=self.code)
#         return RuleResult()   

# class Rule_Previous_Customer(Rule): 
#     def __init__(self): 
#         self.code = "EC100" 
#         self.reason = "DTI <= 43, credit score >= 625 and existing customer"
#     def apply(self, loan: Loan, ctx: dict) -> RuleResult:
#         if ((loan.applicant.debt_to_income_ratio() <= 43) and 
#            (loan.applicant.credit_score and loan.applicant.credit_score >= 625)):  
#             if (loan.applicant.existing_customer): 
#                 ctx[Status.APPROVE].append(self.code)
#                 return RuleResult(apr=MEDIUM, status=Status.APPROVE, code=self.code)
#         return RuleResult()  

# class Rule_Refer(Rule): 
#     def __init__(self): 
#         self.code = "ZC100" 
#         self.reason = "DTI <= 50, credit score >= 700 and existing customer or employed"
#     def apply(self, loan: Loan, ctx: dict) -> RuleResult:
#         if ((loan.applicant.debt_to_income_ratio() <= 50) and 
#            (loan.applicant.credit_score and loan.applicant.credit_score >= 700) and 
#            (loan.applicant.existing_customer or loan.applicant.employment_status)):  
#             ctx[Status.APPROVE].append(self.code)
#             return RuleResult(apr=MEDIUM, status=Status.APPROVE, code=self.code)
#         return RuleResult()  
 