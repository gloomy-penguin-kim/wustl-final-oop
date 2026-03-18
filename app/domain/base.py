from __future__ import annotations

from abc import ABC, abstractmethod


class BaseEntity(ABC):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @abstractmethod
    def validate(self):...