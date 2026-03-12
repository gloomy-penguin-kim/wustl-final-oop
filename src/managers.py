
from datetime import datetime
from decimal import Decimal
from typing import Dict, overload
import uuid

from events import EventLogger
from fileio.applicant_fileio import ApplicantFileIO
from fileio.decsion_fileio import DecisionFileIO
from fileio.loan_fileio import LoanFileIO
from models import Applicant, Decision, Loan, Status


class LoanManager(LoanFileIO): 
    loans: Dict[uuid.UUID, Loan] = {}   
    def __init__(self, events: EventLogger, **kwargs):  
        super().__init__(**kwargs)  
        self.load() 
        self.events_logger = events
        pass
    def new(self, applicant: Applicant, requested_amount: Decimal, term_months: int, purpose: str): 
        loan_id = uuid.uuid4() 
        loan = Loan(loan_id, 
                    applicant=applicant, 
                    requested_amount=requested_amount, 
                    term_months=term_months, 
                    purpose=purpose, 
                    created_at=datetime.now())
        LoanManager.loans[loan_id] = loan 
        self.save_row(loan) 
        self.events_logger.new(event="submitted", loan_id=loan_id)
        return loan 
    def load(self): 
        LoanManager.loans = self.load_file() 
        print("loaded applicants:", len(LoanManager.loans))
    @overload
    def get(self, loan_id: str) -> Loan | None: 
        loan_idd = uuid.UUID(loan_id)
        return self.get(loan_idd)    
    @overload
    def get(self, loan_id: uuid.UUID) -> Loan | None:  
        if loan_id in LoanManager.loans: 
            return LoanManager.loans[loan_id]    

    
class ApplicantManager(ApplicantFileIO): 
    applicants = {}   
    def __init__(self, **kwargs):  
        super().__init__(**kwargs)
        self.load()  
    def new(self, name: str, annual_income: Decimal, monthly_debt: Decimal, 
                      credit_score: int, employment_status: bool, existing_customer: bool):
        app_id = uuid.uuid4() 
        applicant = Applicant(app_id, 
                              name=name, 
                              annual_income=annual_income, 
                              monthly_debt=monthly_debt, 
                              credit_score=credit_score, 
                              employment_status=employment_status, 
                              existing_customer=existing_customer, 
                              created_at=datetime.now())
        ApplicantManager.applicants[app_id] = applicant 
        self.save_row(applicant)
        return applicant 
    def load(self): 
        ApplicantManager.applicants = self.load_file() 
        print("loaded applicants:", len(ApplicantManager.applicants))
    @overload
    def get(self, app_id: str) -> Loan | None: 
        app_idd = uuid.UUID(app_id)
        return self.get(app_idd)    
    @overload
    def get(self, app_id: uuid.UUID) -> Loan | None:  
        if app_id in ApplicantManager.applicants: 
            return ApplicantManager.applicants[app_id]      


class DecisionManager(DecisionFileIO):         
    decisions = {}  
    def __init__(self, events: EventLogger, **kwargs):
        super().__init__(**kwargs) 
        self.events_logger = events  
        self.load() 
    def new(self, loan_id: uuid.UUID | None, status: Status | None, reason_codes: list[str] | None, 
            approved_amount: Decimal | None, apr: Decimal | None, policy: str):
        decision_id = uuid.uuid4() 
        decision = Decision(decision_id,
                            loan_id,  
                            status=status, 
                            reason_codes=reason_codes, 
                            approved_amount=approved_amount,
                            apr=apr, 
                            policy=policy, 
                            created_at=datetime.now())
        DecisionManager.decisions[decision_id] = decision 
        self.save_row(decision)
        self.events_logger.new("decisioned", loan_id)
        return decision 
    def save(self, d: Decision):  
        decision = d.copy()
        DecisionManager.decisions[d.decision_id] = decision  
        self.save_row(decision) 
    def load(self): 
        DecisionManager.decisions = self.load_file() 
    @overload
    def get(self, decision_id: str) -> Decision | None: 
        decision_idd = uuid.UUID(decision_id)
        return self.get(decision_idd)    
    @overload
    def get(self, app_id: uuid.UUID) -> Decision | None:  
        if app_id in DecisionManager.decisions: 
            return DecisionManager.decisions[app_id]  
