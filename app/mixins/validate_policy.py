from __future__ import annotations

from app.mixins.validate_base import ValidateBaseEntity, ValidationError
from app.rules import RULE_REGISTRY
from app.policies.policy_registry import POLICY_REGISTRY


class ValidatePolicyMixin(ValidateBaseEntity):

    def validate(self):
        if not self.version:
            raise ValidationError("Policy Version cannot be blank")
        if self.type not in POLICY_REGISTRY:
            raise ValidationError(f"Policy \"{self.version}\" type \"{self.type}\" is invalid: {self.type}")
        for r in (self.rules or []):
            if r.__class__.__name__ not in RULE_REGISTRY:
                raise ValidationError(f"Policy Rule is invalid: {r.__class__.__name__}")
        super().validate()