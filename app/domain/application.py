from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal
import uuid
from typing import Any

from app.audit import EmitEvent, HashChain
from app.domain.base_entity import BaseEntity
from app.domain.domain_registry import register_domain
from app.mixins.validate_application import ValidateApplicationMixin
from app.domain.applicant import Applicant


class LoanAppInvalidIdError(Exception):
    pass

@register_domain
class LoanApplication(ValidateApplicationMixin, BaseEntity):

    def __init__(
        self,
        applicant: Any,
        requested_amount: Decimal,
        term_months: int,
        purpose: str,
        submitted_at: datetime = None,
        *args,
        **kwargs
    ):
        self._applicant = applicant
        self._requested_amount = requested_amount
        self._term_months = term_months
        self._purpose = purpose
        self._submitted_at = submitted_at
        super().__init__(*args, **kwargs)

        self._applicant = Applicant.to_applicant(self.hash_chain, applicant)


    def submit(self):
        self.submitted_at = datetime.now(UTC)
        self.hash_chain.append({ "event": "SUBMITTED", "id": self.id, "type": self.type })

    def validate(self):
        if not self.is_submitted:
            raise ValueError(f"the application needs to be submitted before being validated: {self.id}")
        super().validate()
        self.hash_chain.append({ "event": "VALIDATED", "id": self.id, "type": self.type })

    def requested_amount_vs_term_months_vs_income(self):  
        return ((self.requested_amount / self.term_months) * 12) / self.applicant.annual_income

    def calculate_monthly_payment(self, annual_rate):
        # Convert annual rate to monthly decimal
        monthly_rate = (annual_rate / 100) / 12
        # Convert years to total number of months
        num_payments = self.term_months

        # Calculate monthly payment using the formula
        payment = (self.requested_amount * monthly_rate * (1 + monthly_rate) ** num_payments) / \
                  ((1 + monthly_rate) ** num_payments - 1)

        return payment

    @classmethod
    def from_dict(cls, hash_chain: HashChain, data):
        print("application", hash_chain)
        obj = super().from_dict(hash_chain, data)
        obj._applicant = Applicant.to_applicant(hash_chain, obj.applicant)
        return obj

    def __str__(self): 
        return f"LoanApplication({self.applicant}, {self.requested_amount}, {self.term_months}, {self.purpose})"

    def raise_not_existing_error(self):
        raise LoanAppInvalidIdError(f"the current loan application record (\"{self.id}\") is invalid according to file persistence: {JsonCrud.filename}")

    @property
    def requested_amount(self) -> Decimal:
        return self._requested_amount
    @requested_amount.setter
    def requested_amount(self, requested_amount: Decimal):
        self._requested_amount = requested_amount
        self._updated_at = datetime.now(UTC)

    @property
    def term_months(self) -> int:
        return self._term_months
    @term_months.setter
    def term_months(self, term_months: int):
        self._term_months = term_months
        self._updated_at = datetime.now(UTC)

    @property
    def purpose(self) -> str:
        return self._purpose
    @purpose.setter
    def purpose(self, purpose: str):
        self._purpose = purpose
        self._updated_at = datetime.now(UTC)

    @property
    def applicant(self) -> Applicant:
        return self._applicant
    @applicant.setter
    def applicant(self, applicant: Any):
        self._applicant = Applicant.to_applicant(applicant)
        self._updated_at = datetime.now(UTC)

    @property
    def submitted_at(self) -> datetime:
        return self._submitted_at
    @submitted_at.setter
    def submitted_at(self, submitted_at: datetime):
        self._submitted_at = submitted_at
        self._updated_at = datetime.now(UTC)

    @property
    def is_submitted(self) -> bool:
        return self.submitted_at is not None

