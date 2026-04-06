from __future__ import annotations

import uuid
from abc import ABC, abstractmethod
from datetime import datetime, UTC
from types import NoneType

from app.audit import EmitEvent
from app.domain.base import Base
from app.mixins.json_serializable import JsonSerializableMixin
from app.mixins.validate_base import ValidateBaseEntity
from app.persistence import JsonCrud

class BaseEntity(ValidateBaseEntity, JsonCrud, JsonSerializableMixin, Base, ABC):


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


    def init(self, **kwargs):
        if not kwargs.get("created_at"):
            JsonCrud.duplicate_check_in_file(self.id, self.type)
            self.updated_at = self.created_at = datetime.now(UTC)
            EmitEvent.emit(event={
                "event": self.type + " Created",
                "id": self.id,
                "date": datetime.now(UTC),
                "data": str(self),
            })


    def isequal(self, other) -> bool:
        if isinstance(other, NoneType): return False
        for i in self.__dict__:
            if self.__getattribute__(i) != getattr(other, i):
                return False
        for i in other.__dict__:
            if self.__getattribute__(i) != getattr(other, i):
                return False
        return True


    def _update_id(self, id: str, type: str):
        super()._update_id(id, type)
        prev_id = self.id
        self._id = id
        self._updated_at = datetime.now(UTC)
        super()._update_id(id, type)
        EmitEvent.emit(event={
            "event": self.type + " ID was Updated",
            "id": id,
            "date": datetime.now(UTC),
            "prev_id": prev_id,
            "data": str(self),
        })