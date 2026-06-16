from __future__ import annotations

import uuid
from abc import ABC, abstractmethod
from datetime import datetime, UTC
from typing import Any

from app.audit import HashChain


class Base(ABC):

    def __init__(self, *args, **kwargs) -> None:
        super().__init__()
        def kwargs2time(tm: Any):
            if not tm or isinstance(tm, datetime):
                return tm
            return datetime.fromisoformat(tm)
        dt = datetime.now(UTC)
        self._created_at = kwargs2time(kwargs.get("created_at")) or dt
        self._updated_at = kwargs2time(kwargs.get("updated_at")) or dt
        self._validated_at = kwargs2time(kwargs.get("validated_at"))
        self._type = kwargs.get("type") or self.__class__.__name__
        self._id = kwargs.get("id") or str(uuid.uuid4())
        self._hash_chain = kwargs.get("hash_chain")

    @property
    def hash_chain(self) -> HashChain:
        return self._hash_chain
    @hash_chain.setter
    def hash_chain(self, value: HashChain):
        if isinstance(value, HashChain):
            self._hash_chain = value

    @property
    def created_at(self) -> datetime:
        return self._created_at
    @created_at.setter
    def created_at(self, value):
        if isinstance(value, str):
            value = datetime.fromisoformat(value)
        self._created_at = value
        self._updated_at = value

    @property
    def updated_at(self) -> datetime:
        return self._updated_at
    @updated_at.setter
    def updated_at(self, value):
        if isinstance(value, str):
            value = datetime.fromisoformat(value)
        self._updated_at = value

    @property
    def validated_at(self) -> datetime:
        return self._validated_at
    @validated_at.setter
    def validated_at(self, value):
        if isinstance(value, str):
            value = datetime.fromisoformat(value)
        self._validated_at = value
        self._updated_at = value

    @property
    def id(self) -> str: return self._id
    @id.setter
    def id(self, value: str):
        self._id = value

    @property
    def type(self) -> str:
        return self._type

    @property
    def is_validated(self) -> bool:
        return self.validated_at is not None and self.validated_at >= self.updated_at
