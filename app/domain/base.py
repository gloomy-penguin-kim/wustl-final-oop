from __future__ import annotations

class BaseEntity:

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def validate(self):
        pass