from __future__ import annotations

from decimal import Decimal
import uuid
from datetime import UTC, datetime
from typing import Any, Tuple

from app.domain.base_entity import BaseEntity
from app.domain.domain_registry import register_domain
from app.mixins.normalize_reason_codes import NormalizeReasonCodesMixin
from app.mixins.validate_decision import ValidateDecisionMixin
from app.rules.rule_status import RuleStatus

@register_domain
class Decision( 
    ValidateDecisionMixin,
    NormalizeReasonCodesMixin,
    BaseEntity
): 

    def __init__(
        self, 
        status: RuleStatus,
        reason_codes: list[str],
        application_id: str,
        application: dict,
        policy_id: str,
        policy: dict,
        approved_amount: Decimal | None = None,
        apr: Decimal | None = None,
        *args,
        **kwargs
    ):
        self._status = status
        self._reason_codes = list(reason_codes)
        self._approved_amount = approved_amount
        self._apr = apr
        self._policy_id = policy_id
        self._policy = policy
        self._application_id = application_id
        self._application = application
        super().__init__(*args, **kwargs)

        if not self.validated_at: self.validate()
    
    def __str__(self): 
        return f"Decision({self.status}, reason_codes={self.reason_codes}, amount={self.approved_amount}, apr={self.apr}, policy={self.policy_id})"

    def isequivalent(self, other: Decision) -> bool:
        if not isinstance(other, Decision):
            return False
        if (self.status == other.status and
            self.reason_codes == other.reason_codes and
            self.approved_amount == other.approved_amount and
            self.apr == other.apr and
            self.policy_id == other.policy_id and
            self.application_id == other.application_id and
            self.application == other.application and
            self.policy == other.policy):
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
    def policy_id(self) -> str:
        return self._policy_id
    @policy_id.setter
    def policy_id(self, value: str):
        self._policy_id = value
        self._updated_at = datetime.now(UTC)

    @property
    def policy(self) -> dict:
        return self._policy
    @policy.setter
    def policy(self, value: dict):
        self._policy = value
        self._updated_at = datetime.now(UTC)

    @property
    def application_id(self) -> str:
        return self._application_id
    @application_id.setter
    def application_id(self, value: str):
        self._application_id = value
        self._updated_at = datetime.now(UTC)

    @property
    def application(self) -> dict:
        return self._application
    @application.setter
    def application(self, value: dict):
        self._application = value
        self._updated_at = datetime.now(UTC)
