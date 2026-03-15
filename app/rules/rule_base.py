from __future__ import annotations

from abc import ABC, abstractmethod

from app.rules.rule_result import RuleResult

class Rule(ABC):

    @abstractmethod
    def apply(self, app, ctx) -> RuleResult:
        pass