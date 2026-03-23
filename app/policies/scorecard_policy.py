from __future__ import annotations
from decimal import ROUND_HALF_UP, Decimal
from typing import Tuple
from datetime import UTC, datetime

from app.domain.application import LoanApplication
from app.domain.decision import Decision
from app.policies.policy_base import Policy
from app.policies.policy_registry import register_policy
from app.rules.rule_base import Rule
from app.rules.rule_result import Status

@register_policy
class ScorecardPolicy(Policy):

    def __init__(self, version: str, rules: list[Rule] | None = None, created_at: datetime | None = None):
        cn = self.__class__.__name__ 
        super().__init__(version=version, type=cn, rules=rules, created_at=created_at)

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
            score += 40
        elif app.applicant.dti() < 0.4:
            reason_codes.append("DTI")
            human.append("debt to income (fair)")
            score += 25
        elif app.applicant.dti() < 0.5:
            reason_codes.append("DTI")
            human.append("debt to income (low)")
            score += 10

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

        ctx = dict(zip(reason_codes, human)) 

        self.policy_evaluated(app)

        if score >= 75:
            return (
                Decision(
                    status = Status.APPROVE,
                    reason_codes = reason_codes,
                    approved_amount = app.requested_amount,
                    apr = Decimal(0.15).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP),
                    policy_version = self.version
                ),
                ctx
            )

        elif score >= 50:
            return (
                Decision(
                    status = Status.REFER,
                    reason_codes = reason_codes,
                    approved_amount = Decimal(0),
                    apr = Decimal(0),
                    policy_version = self.version
                ),
                ctx
            )

        return (
            Decision(
                status = Status.DECLINE,
                reason_codes = reason_codes,
                policy_version = self.version
            ),
            ctx
        )