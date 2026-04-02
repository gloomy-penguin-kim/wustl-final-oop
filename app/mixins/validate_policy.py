from __future__ import annotations

from app.mixins.validate_base import ValidateBaseEntity, ValidationError
from app.rules import RULE_REGISTRY
from app.policies.policy_registry import POLICY_REGISTRY


class ValidatePolicyMixin(ValidateBaseEntity):

    def validate(self):
        if not self.id:
            raise ValidationError("Policy Id cannot be blank")
        # if self.type != "Policy":
        #     raise ValidationError("Type must be 'Policy', instead:", self.type)
        if self.policy not in POLICY_REGISTRY:
            raise ValidationError(f"Policy \"{self.id}\" type \"{self.policy}\" is invalid")
        for r in (self.rules or []):
            if r.__class__.__name__ not in RULE_REGISTRY:
                raise ValidationError(f"Policy Rule is invalid: {r.__class__.__name__}")
        super().validate()