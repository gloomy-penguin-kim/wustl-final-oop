from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal
import uuid
from typing import Any

from app.audit import EmitEvent
from app.domain.base import BaseEntity
from app.mixins.json_serializable import JsonSerializableMixin
from app.mixins.validate_application import ValidateApplicationMixin
from app.domain.applicant import Applicant
from app.persistence import JsonCrud


class LoanAppInvalidIdError(Exception):
    pass


class LoanApplication(JsonSerializableMixin, ValidateApplicationMixin, BaseEntity):

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
        super().__init__(*args, **kwargs)
        self._requested_amount = requested_amount
        self._term_months = term_months
        self._purpose = purpose
        self._applicant = Applicant.to_applicant(applicant)
        self._submitted_at = submitted_at

        self.init(**kwargs)
        self.save()

    def submit(self):
        if not self.existing_id(self.id):
            self.raise_not_existinig_error()
        self.submitted_at = datetime.now(UTC)
        self.save()
    def requested_amount_vs_term_months_vs_income(self):  
        return ((self.requested_amount / self.term_months) * 12) / self.applicant.annual_income

    @classmethod
    def from_dict(cls, data):
        obj = super().from_dict(data)
        obj.applicant = Applicant.to_applicant(obj.applicant)
        return obj

    def __str__(self): 
        return f"LoanApplication({self.applicant}, {self.requested_amount}, {self.term_months}, {self.purpose})"

    def validate(self):
        if not self.existing_id(self.id):
            self.raise_not_existinig_error()
        super().validate()
        self.save()

    def save(self):
        self.save_to_file()

    @classmethod
    def delete(cls, id: str):
        cls.delete_from_file_by_id(id, cls.__name__)

    def raise_not_existinig_error(self):
        raise LoanAppInvalidIdError(f"the current loan application record (\"{self.id}\") is invalid according to file persistence: {JsonCrud.filename}")

    @property
    def requested_amount(self) -> Decimal:
        return self._requested_amount
    @requested_amount.setter
    def requested_amount(self, requested_amount: Decimal):
        self._requested_amount = requested_amount
        self.updated_at = datetime.now(UTC)

    @property
    def term_months(self) -> int:
        return self._term_months
    @term_months.setter
    def term_months(self, term_months: int):
        self._term_months = term_months
        self.updated_at = datetime.now(UTC)

    @property
    def purpose(self) -> str:
        return self._purpose
    @purpose.setter
    def purpose(self, purpose: str):
        self._purpose = purpose
        self.updated_at = datetime.now(UTC)

    @property
    def applicant(self) -> Applicant:
        return self._applicant
    @applicant.setter
    def applicant(self, applicant: Any):
        self._applicant = Applicant.to_applicant(applicant)
        self.updated_at = datetime.now(UTC)

    @property
    def submitted_at(self) -> datetime:
        return self._submitted_at
    @submitted_at.setter
    def submitted_at(self, submitted_at: datetime):
        self._submitted_at = submitted_at
        self.updated_at = datetime.now(UTC)

    @property
    def is_submitted(self) -> bool:
        return self.submitted_at is not None

