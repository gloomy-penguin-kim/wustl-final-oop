from __future__ import annotations

from app.mixins.validate_base import ValidateBaseEntity, ValidationError
from app.rules import RuleStatus


class ValidateDecisionMixin(ValidateBaseEntity):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    def validate(self):
        super().validate()
        if self.status == RuleStatus.DECLINE:
            if self.approved_amount is not None or self.apr is not None:
                raise ValidationError("Decline cannot include requested amount or APR")
        if self.status == RuleStatus.APPROVE:
            if self.approved_amount is None or self.apr is None:
                raise ValidationError("Approve must include requested amount and APR")
            ## TODO uncomment this
        # if self.status == RuleStatus.REFER:
        #     if self.approved_amount is None or self.apr is None:
        #         raise ValueError("REFER must include requested amount and APR")


