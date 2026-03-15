from __future__ import annotations

class ReasonCodeMixin:

    def normalize_reason_codes(self):

        self._reason_codes = tuple(
            sorted(set(self._reason_codes))
        )