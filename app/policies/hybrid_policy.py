from __future__ import annotations

from collections import defaultdict
from decimal import ROUND_HALF_UP, Decimal
from typing import Any, Tuple, cast
from datetime import UTC, datetime

from app.domain import Decision
from app.domain.domain_registry import register_domain
from app.policies.policy_base import Policy
from app.policies.policy_registry import register_policy
from app.rules.rule_base import Rule
from app.domain.application import LoanApplication
from app.rules.rule_registry import RULE_REGISTRY
from app.rules.rule_result import RuleResult
from app.rules.rule_status import RuleStatus


@register_domain
@register_policy
class HybridPolicy(Policy):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __repr__(self):
        return super().__repr__()

    def evaluate(self, app: LoanApplication) -> Tuple[Decision, dict]:
        self.policy_selected(app)

        result = RuleResult(RuleStatus.APPROVE, "")
        ctx = defaultdict(dict)
        reason_codes = []
        apr = Decimal(0.15).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        requested_amount = app.requested_amount

        for rule in self._rules:
            result = rule.apply(app, ctx)
            if result.status == RuleStatus.DECLINE:
                break
            elif result.status == RuleStatus.REFER:
                break

            reason_codes.append(result.code)

        if result.status == RuleStatus.DECLINE:
            apr = None
            requested_amount = None
        elif result.status == RuleStatus.REFER:
            apr = Decimal(0)
            requested_amount = Decimal(0)

        human = ctx[result.status]
        reason_codes = list(human.keys())

        if result.status == RuleStatus.REFER:
            if app.applicant.existing_customer:
                result.status = RuleStatus.APPROVE
                apr = Decimal(0.25).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
                requested_amount = Decimal(0.75) * app.requested_amount

        if result.status == RuleStatus.DECLINE:
            if app.applicant.employment_status != "UNEMPLOYED" and app.applicant.dti() <= 45:
                result.status = RuleStatus.REFER
                apr = Decimal(0)
                requested_amount = Decimal(0)

        self.policy_evaluated(app)
        
        return (
            Decision(
                status=result.status,
                reason_codes=reason_codes,
                approved_amount=requested_amount,
                apr=apr,
                policy_id = self.id,
                policy = self.to_dict(),
                application_id = app.id,
                application = app.to_dict(),
                hash_chain = self.hash_chain,
            ),
            human
        )