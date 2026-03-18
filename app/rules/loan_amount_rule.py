from __future__ import annotations

from app.domain.application import LoanApplication
from app.rules.rule_result import Status, RuleResult
from app.rules.rule_base import Rule
from app.rules.rule_registry import register_rule  

@register_rule
class LoanAmountRule(Rule):
    def __init__(self): 
        self.code = "LA500" 
        self.reason = "monthly disposable income vs monthly payment"

    def apply(self, app: LoanApplication, ctx: dict) -> RuleResult: 
        
        result = RuleResult(Status.DECLINE, self.code)
        reason = self.reason   

        monthly_disposable = app.applicant.income_vs_monthly_debt() 
        monthly_payment = app.requested_amount / app.term_months

        if monthly_disposable > monthly_payment * 4:
            result.status = Status.APPROVE
        
        if monthly_disposable > float(monthly_payment) * 2.5:
            result.status = Status.REFER
          
        ctx[result.status][self.code] = reason  

        return result
     