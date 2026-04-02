from __future__ import annotations
 
from app.rules.rule_base import Rule
from app.rules.rule_result import RuleResult
from app.rules.rule_status import RuleStatus
from app.rules.rule_registry import register_rule  

@register_rule
class CreditScoreRule(Rule):
    def __init__(self):  
        self.code = "CS100"
        self.reason = "credit score check"

    def apply(self, app, ctx) -> RuleResult:
        
        result = RuleResult(RuleStatus.APPROVE, self.code)
        reason = self.reason 

        if app.applicant.credit_score < 550:   
            result.status = RuleStatus.DECLINE
            reason = "low credit score < 550"

        elif app.applicant.credit_score < 625:
            result.status = RuleStatus.REFER
            reason = "low credit score < 625"

        ctx[result.status][self.code] = reason  

        return result
    

 