from __future__ import annotations

from app.rules import Status
from decimal import Decimal

class ValidatableMixin:

    def validate(self):

        if self.status == Status.DECLINE: 
            if self.approved_amount is not None or self.apr is not None:
                raise ValueError("Decline cannot include requested amount or APR")

        if self.status == Status.APPROVE: 
            if self.approved_amount is None or self.apr is None:
                raise ValueError("Approve must include requested amount and APR")

        if self.status == Status.REFER: 
            if self.approved_amount != Decimal(0) or self.apr != Decimal(0):
                raise ValueError("Refer must have 0 for requested amount and APR")

 