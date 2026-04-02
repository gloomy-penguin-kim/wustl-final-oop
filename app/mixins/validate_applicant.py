from __future__ import annotations

from app.mixins.validate_base import ValidateBaseEntity, ValidationError


class ValidateApplicantMixin(ValidateBaseEntity):

    def validate(self):
        if not self.name:
            raise ValidationError("Applicant name required")
        if not (300 <= self.credit_score <= 850):
            raise ValidationError("Invalid credit score")
        if not (self.monthly_debt >= 0):
            raise ValidationError("Invalid monthly debt")
        if not (self.annual_income >= 0):
            raise ValidationError("Invalid annual income")
        if self.created_at is None:
            raise ValidationError("invalid created timestamp")
        super().validate()
