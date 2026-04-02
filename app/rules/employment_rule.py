from __future__ import annotations

from app.rules.rule_base import Rule
from app.rules.rule_registry import register_rule
from app.rules.rule_result import RuleResult
from app.rules.rule_status import RuleStatus

@register_rule
class EmploymentRule(Rule): 
    def __init__(self): 
        self.code = "EM333" 
        self.reason = "employment, income, requested amount check"

    def apply(self, app, ctx: dict) -> RuleResult:
         
        result = RuleResult(RuleStatus.DECLINE, self.code)
        reason = self.reason  

        if app.applicant.employment_status != "EMPLOYED":

            if app.requested_amount_vs_term_months_vs_income() < 0.10: 
                result.status = RuleStatus.APPROVE
                reason = "no employment, but income is high enough"
            elif app.applicant.existing_customer and app.requested_amount_vs_term_months_vs_income() < 0.25/2:
                result.status = RuleStatus.REFER
                reason = "no employment, but existing customer and high enough income"
   
        ctx[result.status][self.code] = reason  

        return result