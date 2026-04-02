from __future__ import annotations

import uuid
from abc import ABC, abstractmethod
from datetime import datetime, UTC
from types import NoneType
from xmlrpc.client import DateTime

from app.audit import EmitEvent
from app.mixins.json_serializable import JsonSerializableMixin
from app.persistence import JsonCrud


class BaseEntity(JsonCrud, ABC):

    def __init__(self, *args, **kwargs):
        super().__init__()
        self._created_at = None
        self._updated_at = None
        self._validated_at = None
        self._type = None
        self._id = None

    def init(self, **kwargs):
        self._created_at = kwargs.get("created_at")
        self._updated_at = kwargs.get("updated_at")
        self._validated_at = kwargs.get("validated_at")
        self._type = self._type or kwargs.get("type")
        self._id = kwargs.get("id")
        if self.id:
            self.duplicate_check(self.created_at)
        else:
            self._id = str(uuid.uuid4())
        if not self.created_at:
            self.updated_at = self.created_at = datetime.now(UTC)
            EmitEvent.emit(event={
                "event": self.type + " Created",
                "id": self.id,
                "date": datetime.now(UTC),
                "data": str(self),
            })

    def duplicate_check(self, created_at):
        if not created_at:
            JsonCrud.duplicate_check_in_file(self.id, self.type)

    def update_id(self, id: str, type: str):
        JsonCrud.duplicate_check_in_file(id, type)
        prev_id = self.id
        self._id = id
        EmitEvent.emit(event={
            "event": self.__class__.__name__ + " ID was Updated",
            "id": id,
            "date": datetime.now(UTC),
            "prev_id": prev_id,
            "data": str(self),
        })

    def isequal(self, other) -> bool:
        if isinstance(other, NoneType): return False
        for i in self.__dict__:
            if self.__getattribute__(i) != getattr(other, i):
                return False
        return True

    @property
    def created_at(self) -> datetime:
        return self._created_at
    @created_at.setter
    def created_at(self, value: datetime):
        self._created_at = value
        self.updated_at = datetime.now(UTC)

    @property
    def updated_at(self) -> datetime:
        return self._updated_at
    @updated_at.setter
    def updated_at(self, value: datetime):
        self._updated_at = value

    @property
    def validated_at(self) -> datetime:
        return self._validated_at
    @validated_at.setter
    def validated_at(self, value: datetime):
        print(self.__class__.__name__ + " validated_at", self.validated_at, value)
        self._validated_at = value
        self.updated_at = datetime.now(UTC)

    @property
    def id(self) -> str: return self._id
    @id.setter
    def id(self, value):
        self.update_id(value, self.type)
        self.updated_at = datetime.now(UTC)
        self._id = value

    @property
    def type(self) -> str:
        return self._type
    @type.setter
    def type(self, value: str):
        self._type = value