from __future__ import annotations

from decimal import Decimal
import uuid
from datetime import UTC, datetime

from app.domain.base import BaseEntity
from app.mixins.json_serializable import JsonSerializableMixin 
from app.mixins.validatable import ValidatableMixin
from app.rules.rule_result import Status

class Decision( 
    ValidatableMixin,
    JsonSerializableMixin,
    BaseEntity
): 

    def __init__(
        self, 
        status: Status,
        policy_version: str,
        reason_codes: list[str],
        approved_amount: Decimal | None = None,
        apr: Decimal | None = None,
        decision_id: str | None = None,
        created_at: datetime = datetime.now(UTC),
        **kwargs
    ):
        super().__init__(**kwargs)

        self.decision_id = decision_id or str(uuid.uuid4())
        self.status = status
        self._reason_codes = list(reason_codes) 
        self.approved_amount = approved_amount
        self.apr = apr
        self.policy_version = policy_version 
        self.created_at = created_at 

        # self.normalize_reason_codes()

        self.validate()
    
    def __eq__(self, other):
        if not isinstance(other, Decision):
            return NotImplemented
        return self.isEqualTo(other)
    
    def __str__(self): 
        return f"Decision({self.status} {self.reason_codes} amount={self.approved_amount}, apr={self.apr}, policy={self.policy_version})"

    @property
    def reason_codes(self):
        return tuple(sorted(set(self._reason_codes))) if self._reason_codes else tuple()

    def validate(self):
        super().validate()
            
    def isEqual(self, other: Decision) -> bool: 
        if not isinstance(other, Decision):
            return False
        if (self.status == other.status and
            self._reason_codes == list(other.reason_codes) and
            self.approved_amount == other.approved_amount and
            self.apr == other.apr and
            self.policy_version == other.policy_version):
            return True  
        return False 
