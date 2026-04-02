from __future__ import annotations

from app.rules.rule_result import RuleResult
from app.rules.rule_status import RuleStatus
from app.rules.rule_base import Rule
from app.rules.rule_registry import register_rule  

@register_rule
class DtiRule(Rule):
    def __init__(self): 
        self.code = "DIT30" 
        self.reason = "DTI check"

    def apply(self, app, ctx: dict) -> RuleResult:

        result = RuleResult(RuleStatus.APPROVE, self.code)
        reason = self.reason 
         
        if app.applicant.dti() >= 0.50:
            result.status = RuleStatus.DECLINE
            reason = "DTI is above 0.50"

        elif app.applicant.dti() > 0.43:
            result.status = RuleStatus.REFER
            reason = "DTI is above 0.43"

        ctx[result.status][self.code] = reason  

        return result