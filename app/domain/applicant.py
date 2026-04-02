from __future__ import annotations

import uuid
from datetime import datetime, UTC 
from decimal import Decimal

from app.mixins.json_serializable import JsonSerializableMixin
from app.mixins.validate_applicant import ValidateApplicantMixin
from app.audit import EmitEvent


class Applicant(JsonSerializableMixin, ValidateApplicantMixin):

    def __init__(
        self,
        name: str,
        annual_income: Decimal,
        monthly_debt: Decimal,
        credit_score: int,
        employment_status: str,
        existing_customer: bool = False,
        created_at: datetime = None,
        validated_at: datetime = None,
        id: str = None,
        **kwargs
    ):
        super().__init__(**kwargs)

        self._name = name
        self._annual_income = annual_income
        self._monthly_debt = monthly_debt
        self._credit_score = credit_score
        self._employment_status = employment_status
        self._existing_customer = existing_customer
        self._created_at = created_at or datetime.now(UTC)
        self._validated_at = validated_at

        self._id = id or str(uuid.uuid4())
        self._type = self.__class__.__name__

        if not created_at:
            EmitEvent.emit(event={
                "event": "Applicant Created",
                "date": datetime.now(UTC),
                "data": str(self),
                "id": self.id
            })

        if not self.validated_at: self.validate()

    def dti(self):
        if self.annual_income == 0:
            return 1
        return (self.monthly_debt * 12) / self.annual_income
    
    def income_vs_monthly_debt(self): 
        return (self.annual_income / 12) - self.monthly_debt
        
    def __str__(self): 
        return f"Applicant(name={self.name}, income={self.annual_income}, credit_score={self.credit_score}, employment={self.employment_status}, existing_customer={self.existing_customer})"

    def isequal(self, other: Applicant) -> bool:
        if not isinstance(other, Applicant):
            return NotImplemented
        for i in self.__dict__:
            if self.__getattribute__(i) != getattr(other, i):
                return False
        return True

    @classmethod
    def to_applicant(cls, applicant) -> Applicant | None:
        if isinstance(applicant, str):
            applicant = Applicant.from_json(applicant)
        if isinstance(applicant, dict):
            applicant = Applicant.from_dict(applicant)
        assert applicant is None or isinstance(applicant, Applicant)
        return applicant

    @property
    def name(self): return self._name
    @name.setter
    def name(self, value): self._name = value

    @property
    def annual_income(self): return self._annual_income
    @annual_income.setter
    def annual_income(self, value): self._annual_income = value

    @property
    def monthly_debt(self): return self._monthly_debt
    @monthly_debt.setter
    def monthly_debt(self, value): self._monthly_debt = value

    @property
    def credit_score(self): return self._credit_score
    @credit_score.setter
    def credit_score(self, value): self._credit_score = value

    @property
    def employment_status(self): return self._employment_status
    @employment_status.setter
    def employment_status(self, value): self._employment_status = value

    @property
    def existing_customer(self): return self._existing_customer
    @existing_customer.setter
    def existing_customer(self, value): self._existing_customer = value

    @property
    def created_at(self): return self._created_at
    @created_at.setter
    def created_at(self, value): self._created_at = value

    @property
    def validated_at(self): return self._validated_at
    @validated_at.setter
    def validated_at(self, value): self._validated_at = value

    @property
    def id(self): return self._id
    @id.setter
    def id(self, value): self._id = value

    @property
    def type(self): return self._type
    @type.setter
    def type(self, value): self._type = value