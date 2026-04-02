from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal
import uuid
from typing import Any

from app.audit import EmitEvent, HashChain
from app.mixins.json_serializable import JsonSerializableMixin
from app.mixins.validate_application import ValidateApplicationMixin
from app.domain.applicant import Applicant
from app.persistence import JsonCrud


class LoanApplication(JsonSerializableMixin, ValidateApplicationMixin, JsonCrud):

    def __init__(
        self,
        applicant: Any,
        requested_amount: Decimal,
        term_months: int,
        purpose: str,
        application_id: str | None = None,
        created_at: datetime = None,
        submitted_at: datetime = None,
        validated_at: datetime = None,
        id: str = None,
        type: str = None,
    ):
        super().__init__()

        JsonCrud.duplicate_check(application_id)

        self._application_id = application_id or str(uuid.uuid4())
        self._requested_amount = requested_amount
        self._term_months = term_months
        self._purpose = purpose
        self._applicant = Applicant.to_applicant(applicant)
        self._created_at = created_at or datetime.now(UTC)
        self._submitted_at = submitted_at
        self._validated_at = validated_at
        self._type = self.__class__.__name__

        self._id = id or self.application_id

        self.save()

        if not created_at:
            EmitEvent.emit(event={
                "event": "Application Created",
                "date": datetime.now(UTC),
                "data": str(self),
                "id": self.id
            })

    def submit(self):
        self.submitted_at = datetime.now(UTC)
        HashChain.append({
            "event": "SUBMITTED",
            "date": datetime.now(UTC),
            "data": self.to_dict(),
            "id": self.id
        })

    def validate(self):
        super().validate()
        HashChain.append({
            "event": "VALIDATED",
            "date": datetime.now(UTC),
            "data": self.to_dict(),
            "id": self.id
        })

    def requested_amount_vs_term_months_vs_income(self):  
        return ((self.requested_amount / self.term_months) * 12) / self.applicant.annual_income

    @classmethod
    def from_dict(cls, data):
        obj = super().from_dict(data)
        obj.applicant = Applicant.to_applicant(obj.applicant)
        return obj

    
    def __str__(self): 
        return f"LoanApplication({self.applicant}, amount={self.requested_amount}, term_months={self.term_months}, purpose={self.purpose})"

    def save(self):
        self.save_to_file()

    @classmethod
    def delete(cls, application_id):
        cls.delete_from_file_by_id(application_id)


    @property
    def application_id(self) -> str:
        return self._application_id
    @application_id.setter
    def application_id(self, application_id: str):
        LoanApplication.duplicate_check(application_id)
        self._application_id = application_id
        self._id = application_id

    @property
    def requested_amount(self) -> Decimal:
        return self._requested_amount
    @requested_amount.setter
    def requested_amount(self, requested_amount: Decimal):
        self._requested_amount = requested_amount
        self.validate()

    @property
    def term_months(self) -> int:
        return self._term_months
    @term_months.setter
    def term_months(self, term_months: int):
        self._term_months = term_months
        self.validate()

    @property
    def purpose(self) -> str:
        return self._purpose
    @purpose.setter
    def purpose(self, purpose: str):
        self._purpose = purpose

    @property
    def applicant(self) -> Applicant:
        return self._applicant
    @applicant.setter
    def applicant(self, applicant: Any):
        self._applicant = Applicant.to_applicant(applicant)

    @property
    def created_at(self) -> datetime:
        return self._created_at
    @created_at.setter
    def created_at(self, created_at: datetime):
        self._created_at = created_at

    @property
    def submitted_at(self) -> datetime:
        return self._submitted_at
    @submitted_at.setter
    def submitted_at(self, submitted_at: datetime):
        self._submitted_at = submitted_at

    @property
    def validated_at(self) -> datetime:
        return self._validated_at
    @validated_at.setter
    def validated_at(self, validated_at: datetime):
        self._validated_at = validated_at

    @property
    def id(self): return self._id
    @id.setter
    def id(self, value):
        LoanApplication.duplicate_check(value)
        self._id = value
        self.application_id = value

    @property
    def type(self): return self._type
    @type.setter
    def type(self, value):
        self._type = value
