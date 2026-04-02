from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from app.rules.rule_result import RuleResult

if TYPE_CHECKING:
    from app.domain import LoanApplication

class Rule(ABC):

    @abstractmethod
    def apply(self, app: "LoanApplication", ctx: dict) -> RuleResult:...