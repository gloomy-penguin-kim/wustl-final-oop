from __future__ import annotations

from app.mixins.validate_base import ValidateBaseEntity, ValidationError


class ValidateApplicationMixin(ValidateBaseEntity):

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    def validate(self):
        super().validate()
        if self.requested_amount <= 0:
            raise ValidationError("Invalid loan amount")
        if self.term_months not in {12, 24, 36, 48, 60}:
            raise ValidationError("Invalid loan term")
        if not self.purpose:
            raise ValidationError("Invalid purpose")
        if isinstance(self.applicant, str) or isinstance(self.applicant, dict):
            raise ValidationError("Invalid applicant")

