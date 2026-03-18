from __future__ import annotations
from datetime import UTC

from app.mixins.json_serializable import JsonSerializableMixin
from datetime import datetime
from decimal import Decimal
import uuid 


class Applicant(JsonSerializableMixin):
    def __init__(
        self,
        name: str,
        annual_income: Decimal,
        monthly_debt: Decimal,
        credit_score: int,
        employment_status: str,
        existing_customer=False,
        created_at: datetime = datetime.now(UTC) 
    ): 
        self.name = name
        self.annual_income = annual_income
        self.monthly_debt = monthly_debt
        self.credit_score = credit_score
        self.employment_status = employment_status
        self.existing_customer = existing_customer
        self.created_at = created_at 

        self.validate()

    def dti(self):
        if self.annual_income == 0:
            return 1
        return (self.monthly_debt * 12) / self.annual_income
    
    def income_vs_monthly_debt(self): 
        return (self.annual_income / 12) - self.monthly_debt

    def validate(self):
        if not self.name:
            raise ValueError("Applicant name required")

        if not (300 <= self.credit_score <= 850):
            raise ValueError("Invalid credit score")
        
    def __str__(self): 
        return f"Applicant({self.name}, {self.annual_income}, {self.credit_score}, {self.employment_status}, {self.existing_customer})"