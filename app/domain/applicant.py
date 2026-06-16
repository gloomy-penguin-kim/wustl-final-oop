from __future__ import annotations

import uuid
from datetime import datetime, UTC 
from decimal import Decimal

from app.audit import HashChain
from app.domain.base_entity import BaseEntity
from app.mixins.json_serializable import JsonSerializableMixin
from app.mixins.validate_applicant import ValidateApplicantMixin


class Applicant(ValidateApplicantMixin, BaseEntity):

    def __init__(
        self,
        name: str,
        annual_income: Decimal,
        monthly_debt: Decimal,
        credit_score: int,
        employment_status: str,
        existing_customer: bool = False,
        *args,
        **kwargs
    ):
        self._name = name
        self._annual_income = annual_income
        self._monthly_debt = monthly_debt
        self._credit_score = credit_score
        self._employment_status = employment_status
        self._existing_customer = existing_customer
        super().__init__(*args, **kwargs)

        if not self.validated_at: self.validate()

    def validate(self):
        super().validate()

    def __eq__(self, other: Applicant):
        if isinstance(other, Applicant):
            return self.isequal(other)
        return False

    def dti(self):
        if self.annual_income == 0:
            return 1
        return (self.monthly_debt * 12) / self.annual_income
    
    def income_vs_monthly_debt(self): 
        return (self.annual_income / 12) - self.monthly_debt
        
    def __str__(self): 
        return f"Applicant(name={self.name}, income={self.annual_income}, credit_score={self.credit_score}, employment={self.employment_status}, existing_customer={self.existing_customer})"

    @classmethod
    def to_applicant(cls, hash_chain: HashChain, applicant) -> Applicant | None:
        if isinstance(applicant, str):
            applicant = Applicant.from_json(hash_chain, applicant)
        if isinstance(applicant, dict):
            applicant = Applicant.from_dict(hash_chain, applicant)
        assert applicant is None or isinstance(applicant, Applicant)
        return applicant

    @property
    def name(self) -> str:
        return self._name
    @name.setter
    def name(self, value: str):
        self._name = value
        self._updated_at = datetime.now()

    @property
    def annual_income(self) -> Decimal:
        return self._annual_income
    @annual_income.setter
    def annual_income(self, value: Decimal):
        self._annual_income = value
        self._updated_at = datetime.now()

    @property
    def monthly_debt(self) -> Decimal:
        return self._monthly_debt
    @monthly_debt.setter
    def monthly_debt(self, value: Decimal):
        self._monthly_debt = value
        self._updated_at = datetime.now()

    @property
    def credit_score(self) -> int:
        return self._credit_score
    @credit_score.setter
    def credit_score(self, value: int):
        self._credit_score = value
        self._updated_at = datetime.now()

    @property
    def employment_status(self) -> str:
        return self._employment_status
    @employment_status.setter
    def employment_status(self, value: str):
        self._employment_status = value
        self._updated_at = datetime.now()

    @property
    def existing_customer(self) -> bool:
        return self._existing_customer
    @existing_customer.setter
    def existing_customer(self, value: bool):
        self._existing_customer = value
        self._updated_at = datetime.now()

