from __future__ import annotations

from datetime import datetime, UTC

from app.domain.base import Base
from app.persistence import JsonCrud


class ValidationError(Exception):
    pass


class ValidateBaseEntity(Base):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    def validate(self):
        if self.id is None:
            raise ValidationError("Class instance attribute \"id\" is None")
        if self.type is None:
            raise ValidationError("Class instance attribute \"type\" is None")
        if self.created_at is None:
            raise ValidationError("Invalid created timestamp")
        self.validated_at = datetime.now(UTC)

    def _update_id(self, id: str, type: str):
        JsonCrud.duplicate_check_in_file(id, type)