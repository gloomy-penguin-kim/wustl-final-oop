from __future__ import annotations
from decimal import ROUND_HALF_UP, Decimal
from typing import Tuple, Any
from datetime import UTC, datetime

from app.domain.application import LoanApplication
from app.domain.decision import Decision
from app.domain.domain_registry import register_domain
from app.policies.policy_base import Policy
from app.policies.policy_registry import register_policy
from app.rules.rule_base import Rule
from app.rules.rule_status import RuleStatus

@register_domain
@register_policy
class ScorecardPolicy(Policy):

    def __init__(self, rules: Any = None, **kwargs):
        super().__init__(rules=rules, **kwargs)

    def __repr__(self):
        return super().__repr__()

    def evaluate(self, app: LoanApplication) -> Tuple[Decision, dict]:
        self.policy_selected(app)

        score = 0
        reason_codes = [] 
        human = [] 

        if app.applicant.credit_score > 720:
            human.append("credit card score (high)")
            reason_codes.append("CCHIGH")
            score += 40
        elif app.applicant.credit_score > 625:
            human.append("credit card score (medium)")
            reason_codes.append("CCMED")
            score += 25 
        elif app.applicant.credit_score > 575:
            human.append("credit card score (low)")
            reason_codes.append("CCLOW")
            score += 10 
        elif app.applicant.credit_score > 500:
            human.append("credit card score (very low)")
            reason_codes.append("CCVLW")
            score += 5

        if app.applicant.dti() < 0.3:
            reason_codes.append("DTI")
            human.append("debt to income (good)")
            score += 20
        elif app.applicant.dti() < 0.4:
            reason_codes.append("DTI")
            human.append("debt to income (fair)")
            score += 15
        elif app.applicant.dti() < 0.5:
            reason_codes.append("DTI")
            human.append("debt to income (low)")
            score -= 10

        if app.applicant.employment_status: 
            reason_codes.append("EMP")
            human.append("employed")
            score += 20 
        else: 
            reason_codes.append("UNEMP")
            human.append("unemployed")
         
        if app.applicant.existing_customer: 
            reason_codes.append("EC")
            human.append("existing customer")
            score += 10
        else: 
            reason_codes.append("NOTEC")
            human.append("not existing customer")

        if app.requested_amount <= 7500: 
            reason_codes.append("LOWAMT")
            human.append("existing customer")
            score += 10

        if app.applicant.income_vs_monthly_debt() >= app.calculate_monthly_payment(Decimal(0.08)):
            score += 20
        else:
            score -= 30

        ctx = dict(zip(reason_codes, human)) 

        self.policy_evaluated(app)

        if score >= 65:
            return (
                Decision(
                    status = RuleStatus.APPROVE,
                    reason_codes = reason_codes,
                    approved_amount = app.requested_amount,
                    apr = Decimal(0.08).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP),
                    policy_id = self.id,
                    policy = self.to_dict(),
                    application_id = app.id,
                    application = app.to_dict(),
                    hash_chain=self.hash_chain,
                ),
                ctx
            )

        elif score >= 45:
            return (
                Decision(
                    status = RuleStatus.REFER,
                    reason_codes = reason_codes,
                    approved_amount = Decimal(0),
                    apr = Decimal(0),
                    policy_id = self.id,
                    policy = self.to_dict(),
                    application_id = app.id,
                    application = app.to_dict(),
                    hash_chain=self.hash_chain,
                ),
                ctx
            )

        return (
            Decision(
                status = RuleStatus.DECLINE,
                reason_codes = reason_codes,
                policy_id = self.id,
                policy = self.to_dict(),
                application_id = app.id,
                application = app.to_dict(),
                hash_chain=self.hash_chain,
            ),
            ctx
        )