from __future__ import annotations

from decimal import Decimal
import uuid
from datetime import UTC, datetime
from typing import Any, Tuple

from app.domain.base_entity import BaseEntity
from app.mixins.normalize_reason_codes import NormalizeReasonCodesMixin
from app.mixins.validate_decision import ValidateDecisionMixin
from app.rules.rule_status import RuleStatus

class Decision( 
    ValidateDecisionMixin,
    NormalizeReasonCodesMixin,
    BaseEntity
): 

    def __init__(
        self, 
        status: RuleStatus,
        policy_version: str,
        reason_codes: list[str],
        approved_amount: Decimal | None = None,
        apr: Decimal | None = None,
        *args,
        **kwargs
    ):
        super().__init__(*args, **kwargs)

        self._status = status
        self._reason_codes = list(reason_codes) 
        self._approved_amount = approved_amount
        self._apr = apr
        self._policy_version = policy_version

        self.init(**kwargs)
        if not self.validated_at: self.validate()
    
    def __str__(self): 
        return f"Decision({self.status}, reason_codes={self.reason_codes}, amount={self.approved_amount}, apr={self.apr}, policy={self.policy_version})"

    def isequivalent(self, other: Decision) -> bool:
        if not isinstance(other, Decision):
            return False
        if (self.status == other.status and
            self.reason_codes == other.reason_codes and
            self.approved_amount == other.approved_amount and
            self.apr == other.apr and
            self.policy_version == other.policy_version):
            return True
        return False

    @property
    def status(self) -> RuleStatus:
        return self._status
    @status.setter
    def status(self, value: RuleStatus):
        self._status = value
        self._updated_at = datetime.now(UTC)

    @property
    def reason_codes(self) -> Tuple[str]:
        return self.normalize_reason_codes()
    @reason_codes.setter
    def reason_codes(self, value: Any):
        self._reason_codes = list(value)
        self._updated_at = datetime.now(UTC)

    @property
    def approved_amount(self) -> Decimal:
        return self._approved_amount
    @approved_amount.setter
    def approved_amount(self, value: Decimal):
        self._approved_amount = value
        self._updated_at = datetime.now(UTC)

    @property
    def apr(self) -> Decimal:
        return self._apr
    @apr.setter
    def apr(self, value: Decimal):
        self._apr = value
        self._updated_at = datetime.now(UTC)

    @property
    def policy_version(self) -> str:
        return self._policy_version
    @policy_version.setter
    def policy_version(self, value: str):
        self._policy_version = value
        self._updated_at = datetime.now(UTC)
