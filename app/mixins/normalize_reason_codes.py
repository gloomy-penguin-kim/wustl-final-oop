from datetime import datetime
from typing import Tuple


class NormalizeReasonCodesMixin:

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    def validate(self):
        assert self.reason_codes == self.normalize_reason_codes()

    def normalize_reason_codes(self) -> Tuple[str]:
        return tuple(sorted(set(self._reason_codes))) if len(self._reason_codes) > 0 else tuple()

    @property
    def reason_codes(self):
        return self.normalize_reason_codes()
    @reason_codes.setter
    def reason_codes(self, value: Tuple[str]):
        self._reason_codes = list(value)
        self.updated_at = datetime.now()
