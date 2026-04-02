from __future__ import annotations 

from collections import defaultdict
from decimal import ROUND_HALF_UP, Decimal
from typing import Any, Tuple, cast
from datetime import UTC, datetime

from app.domain.decision import Decision
from app.policies.policy_base import Policy 
from app.policies.policy_registry import register_policy 
from app.rules.rule_base import Rule
from app.domain.application import LoanApplication
from app.rules.rule_registry import RULE_REGISTRY
from app.rules.rule_result import RuleResult
from app.rules.rule_status import RuleStatus

@register_policy 
class RuleBasedPolicy(Policy):

    def __init__(self, rules: Any = None, **kwargs):
        rr = []
        if Policy.is_list_of_strings(rules):
            r = [] 
            for s in (rules or []): 
                r.append(RULE_REGISTRY[s]())
            rr = r   
        else:
            rr = cast(list[Rule], rules) 
        super().__init__(rules=rr, **kwargs)

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
                apr = None 
                requested_amount = None 
                break 
            elif result.status == RuleStatus.REFER:
                apr = Decimal(0) 
                requested_amount = Decimal(0) 
                break

            reason_codes.append(result.code)
 
        human = ctx[result.status]
        reason_codes = list(human.keys())

        self.policy_evaluated(app)

        return (
            Decision(
                status = result.status,
                reason_codes = reason_codes,
                approved_amount = requested_amount,
                apr = apr,
                policy_version = self.id
            ),
            human
        )