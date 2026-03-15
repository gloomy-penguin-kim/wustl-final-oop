from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal
import uuid

from app.mixins.json_serializable import JsonSerializableMixin
from app.domain.applicant import Applicant


class LoanApplication(JsonSerializableMixin):
    def __init__(
        self,  
        applicant: Applicant,
        requested_amount: Decimal,
        term_months: int,
        purpose: str,
        application_id: str | None = None,
        submitted_at: datetime = datetime.now(UTC)
    ): 
        __slots__ = ['applicant','requested_amount','term_months',
                     'purpose','application_id','submitted_at']
        self.application_id = application_id or str(uuid.uuid4())
        self.submitted_at = submitted_at 
        self.applicant = applicant
        self.requested_amount = requested_amount
        self.term_months = term_months
        self.purpose = purpose 

        self.validate()

    def validate(self):

        if self.requested_amount <= 0:
            raise ValueError("Invalid loan amount")

        if self.term_months not in {12, 24, 36, 48, 60}:
            raise ValueError("Invalid loan term") 

        if not self.purpose:
            raise ValueError("Invalid purpose") 
    
    def requested_amount_vs_term_months_vs_income(self):  
        return ((self.requested_amount / self.term_months) * 12) / self.applicant.annual_income
 
    @classmethod
    def from_dict(cls, data): 
        data = dict(data) 
        data["applicant"] = Applicant.from_dict(data["applicant"]) 
        data["submitted_at"] = datetime.fromisoformat(data["submitted_at"]) if "submitted_at" in data else datetime.now(UTC) 
        data["requested_amount"] = Decimal(data["requested_amount"]) 
        return cls(**data)
    
    def __str__(self): 
        return f"LoanApplication({self.applicant}, {self.requested_amount}, {self.term_months}, {self.purpose})"