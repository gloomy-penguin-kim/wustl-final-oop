from __future__ import annotations

from decimal import Decimal
import uuid
from datetime import UTC, datetime

from app.audit import EmitEvent
from app.domain.base import BaseEntity
from app.mixins.json_serializable import JsonSerializableMixin 
from app.mixins.validate_decision import ValidateDecisionMixin
from app.rules.rule_status import RuleStatus

class Decision( 
    ValidateDecisionMixin,
    JsonSerializableMixin,
    BaseEntity
): 

    def __init__(
        self, 
        status: RuleStatus,
        policy_version: str,
        reason_codes: list[str],
        approved_amount: Decimal | None = None,
        apr: Decimal | None = None,
        id: str | None = None,
        created_at: datetime = datetime.now(UTC),
        **kwargs
    ):
        super().__init__(**kwargs)

        self._id = id or str(uuid.uuid4())
        self._status = status
        self._reason_codes = list(reason_codes) 
        self._approved_amount = approved_amount
        self._apr = apr
        self._policy_version = policy_version
        self._created_at = created_at
        self._type = self.__class__.__name__

        if not created_at:
            EmitEvent.emit(event={
                "event": "Decision Created",
                "date": datetime.now(UTC),
                "data": str(self),
                "id": self.id
            })
        self.validate()

    
    def __eq__(self, other):
        if not isinstance(other, Decision):
            return NotImplemented
        return self.isequal(other)
    
    def __str__(self): 
        return f"Decision({self.status}, reason_codes={self.reason_codes}, amount={self.approved_amount}, apr={self.apr}, policy={self.policy_version})"


    def isequal(self, other: Decision) -> bool:
        if not isinstance(other, Decision):
            return False
        if (self.status == other.status and
            self._reason_codes == list(other.reason_codes) and
            self.approved_amount == other.approved_amount and
            self.apr == other.apr and
            self.policy_version == other.policy_version):
            return True  
        return False

    @property
    def id(self):
        return self._id
    @id.setter
    def id(self, value):
        self._id = value

    @property
    def status(self):
        return self._status
    @status.setter
    def status(self, value):
        self._status = value

    @property
    def reason_codes(self):
        return tuple(sorted(set(self._reason_codes))) if self._reason_codes else tuple()
    @reason_codes.setter
    def reason_codes(self, value):
        self._reason_codes = list(value)

    @property
    def approved_amount(self):
        return self._approved_amount
    @approved_amount.setter
    def approved_amount(self, value):
        self._approved_amount = value

    @property
    def apr(self):
        return self._apr
    @apr.setter
    def apr(self, value):
        self._apr = value

    @property
    def policy_version(self):
        return self._policy_version
    @policy_version.setter
    def policy_version(self, value):
        self._policy_version = value

    @property
    def created_at(self):
        return self._created_at
    @created_at.setter
    def created_at(self, value):
        self._created_at = value

    @property
    def type(self):
        return self._type
    @type.setter
    def type(self, value):
        self._type = value
