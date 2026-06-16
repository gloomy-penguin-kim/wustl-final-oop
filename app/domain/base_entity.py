from __future__ import annotations

from datetime import datetime, UTC
from types import NoneType

from app.audit import EmitEvent
from app.domain.base import Base
from app.mixins.json_serializable import JsonSerializableMixin
from app.mixins.validate_base import ValidateBaseEntity

class BaseEntity(ValidateBaseEntity, JsonSerializableMixin, Base):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not kwargs.get("created_at"):
            self.updated_at = self.created_at = datetime.now(UTC)
            EmitEvent.emit(event={
                "event": self.type + " Created",
                "id": self.id,
                "date": datetime.now(UTC),
                "data": str(self),
            })

    def export(self, filename):
        with open(filename, "a") as f:
            f.write(self.to_json()+"\n")
            self.hash_chain.append({ "event": "EXPORTED", "id": self.id, "type": self.type })

    def isequal(self, other) -> bool:
        if isinstance(other, NoneType): return False
        for i in self.__dict__:
            if i == "_rules":
                if self.rules_as_strings != other.rules_as_strings:
                    return False
            elif self.__getattribute__(i) != getattr(other, i):
                # print(i)
                # print(self.__getattribute__(i))
                # print(other.__getattribute__(i))
                return False
        return True
