from __future__ import annotations
from enum import Enum
import json

from app.mixins.json_serializable import JsonSerializableMixin


class RuleStatus(JsonSerializableMixin, Enum):
    APPROVE = "APPROVE"
    DECLINE = "DECLINE"
    REFER = "REFER"

    def to_dict(self):
        return self.value

    # @classmethod
    # def from_dict(cls, value):
    #     return cls(value)
    #
    # @classmethod
    # def from_json(cls, s):
    #     return cls.from_dict(json.loads(s))