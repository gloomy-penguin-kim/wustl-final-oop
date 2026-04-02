from __future__ import annotations

from app.mixins.validate_base import ValidateBaseEntity, ValidationError


class ValidateApplicationMixin(ValidateBaseEntity):

    @property
    def is_submitted(self) -> bool:
        return self.submitted_at is not None

    def validate(self):
        if not (self.requested_amount > 0):
            raise ValidationError("Invalid loan amount")
        if self.term_months not in {12, 24, 36, 48, 60}:
            raise ValidationError("Invalid loan term")
        if not self.purpose:
            raise ValidationError("Invalid purpose")
        if self.created_at is None:
            raise ValidationError("invalid created timestamp")
        if isinstance(self.applicant, str) or isinstance(self.applicant, dict):
            raise ValidationError("Invalid applicant")

        super().validate()
