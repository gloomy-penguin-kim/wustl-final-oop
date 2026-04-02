from __future__ import annotations

from abc import abstractmethod, ABC
from datetime import datetime, UTC

class ValidationError(Exception):
    pass

class ValidateBaseEntity(ABC):
    @property
    def is_valid(self) -> bool: return self.is_validated is not None
    @property
    def is_validated(self) -> bool: return self.is_validated

    def validate(self):
        if self.id is None:
            raise ValidationError("Class instance attribute \"id\" is None")
        if self.type is None:
            raise ValidationError("Class instance attribute \"type\" is None")
        self.validated_at = datetime.now(UTC)