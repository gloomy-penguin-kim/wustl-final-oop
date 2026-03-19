from __future__ import annotations

from collections import defaultdict
from decimal import ROUND_HALF_UP, Decimal
from typing import Any, Tuple, cast
from datetime import UTC, datetime

from app.domain import Decision
from app.policies.policy_base import Policy
from app.policies.policy_registry import register_policy
from app.rules.rule_base import Rule
from app.domain.application import LoanApplication
from app.rules.rule_registry import RULE_REGISTRY
from app.rules.rule_result import Status, RuleResult


@register_policy
class HybridPolicy(Policy):

    def __init__(self, version: str, rules):
        cn = self.__class__.__name__
        rr = []
        if Policy.is_list_of_strings(rules):
            r = []
            for s in (rules or []):
                r.append(RULE_REGISTRY[s]())
            rr = r
        else:
            rr = cast(list[Rule], rules)
        super().__init__(version=version, type=cn, rules=rr)

    def evaluate(self, app: LoanApplication) -> Tuple[Decision, dict]:
        result = RuleResult(Status.APPROVE, "")
        ctx = defaultdict(dict)
        reason_codes = []
        apr = Decimal(0.15).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        requested_amount = app.requested_amount

        for rule in self._rules:
            result = rule.apply(app, ctx)
            if result.status == Status.DECLINE:
                break
            elif result.status == Status.REFER:
                break

            reason_codes.append(result.code)

        if result.status == Status.DECLINE:
            apr = None
            requested_amount = None
        elif result.status == Status.REFER:
            apr = Decimal(0)
            requested_amount = Decimal(0)

        human = ctx[result.status]
        reason_codes = list(human.keys())

        if result.status == Status.REFER:
            if app.applicant.existing_customer:
                result.status = Status.APPROVE
                apr = Decimal(0.25).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
                requested_amount = Decimal(0.75) * app.requested_amount

        if result.status == Status.DECLINE:
            if app.applicant.employment_status != "UNEMPLOYED" and app.applicant.dti() <= 45:
                result.status = Status.REFER
                apr = Decimal(0)
                requested_amount = Decimal(0)

        self.emit({
            "event": "POLICY_EVALUATED",
            "id": app.application_id + "_" + self.version + "_" + datetime.now(UTC).isoformat(),
            "application_id": app.application_id,
            "policy_version": self.version
        })

        return (
            Decision(
                status=result.status,
                reason_codes=reason_codes,
                approved_amount=requested_amount,
                apr=apr,
                policy_version=self.version
            ),
            human
        )