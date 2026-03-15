from __future__ import annotations

from app.domain.application import LoanApplication
from app.rules.rule_result import Status, RuleResult
from app.rules.rule_base import Rule
from app.rules.rule_registry import register_rule  

@register_rule
class DtiRule(Rule):
    def __init__(self): 
        self.code = "DIT30" 
        self.reason = "DTI check"

    def apply(self, app: LoanApplication, ctx: dict) -> RuleResult:
         
        result = RuleResult(Status.APPROVE, self.code)
        reason = self.reason 
         
        if app.applicant.dti() >= 0.50:
            result.status = Status.DECLINE
            reason = "DTI is above 0.50"

        elif app.applicant.dti() > 0.43:
            result.status = Status.REFER
            reason = "DTI is above 0.43"

        ctx[result.status][self.code] = reason  

        return result