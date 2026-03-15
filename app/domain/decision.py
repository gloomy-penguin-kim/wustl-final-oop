from __future__ import annotations

from decimal import Decimal
import uuid
from datetime import UTC, datetime

from app.domain.base import BaseEntity
from app.mixins.json_serializable import JsonSerializableMixin
from app.mixins.reason_codes import ReasonCodeMixin
from app.mixins.validatable import ValidatableMixin
from app.rules.rule_result import Status

class Decision(
    ReasonCodeMixin,
    ValidatableMixin,
    JsonSerializableMixin,
    BaseEntity
):

    def __init__(
        self,
        *,
        status: Status,
        reason_codes: list[str],
        approved_amount: Decimal | None = None,
        apr: Decimal | None = None,
        policy_version: str,
        decision_id: str | None = None,
        created_at: datetime = datetime.now(UTC)
    ):

        super().__init__()
        self.decision_id = decision_id or str(uuid.uuid4())
        self.status = status
        self._reason_codes = list(reason_codes) 
        self.approved_amount = approved_amount
        self.apr = apr
        self.policy_version = policy_version 
        self.created_at = created_at 

        self.normalize_reason_codes()
        self.validate()
    
    def __str__(self): 
        return f"Decision({self.status} {self.reason_codes} amount={self.approved_amount}, apr={self.apr}, policy={self.policy_version})"

    @property
    def reason_codes(self):
        return tuple(self._reason_codes)

    def validate(self):

        super().validate()

        if self.status == Status.DECLINE:

            if self.approved_amount is not None or self.apr is not None:
                raise ValueError("Decline cannot include requested amount or APR")

        if self.status == Status.APPROVE:

            if self.approved_amount is None or self.apr is None:
                raise ValueError("Approve must include requested amount and APR")

        if self.status == Status.REFER:

            if self.approved_amount != Decimal(0) or self.apr != Decimal(0):
                raise ValueError("Refer must have 0 for requested amount and APR")