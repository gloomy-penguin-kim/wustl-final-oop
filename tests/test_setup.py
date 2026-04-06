from app.audit import HashChain, EmitEvent
from app.persistence import JsonCrud
from app.rules import Rule, RuleResult, RuleStatus
from app.rules.rule_registry import register_rule

hc = HashChain("tests/output/test_audit.jsonl")
hc.clear()
ee = EmitEvent("tests/output/test_events.jsonl")
ee.clear()
jc = JsonCrud("tests/output/test_persistence.jsonl")
jc.clear()


@register_rule
class RuleToReturnRefer(Rule):
    def __init__(self):
        self.code = "RF_TEST"
        self.reason = "refer test for rule codes"

    def apply(self, app, ctx) -> RuleResult:
        result = RuleResult(RuleStatus.REFER, self.code)
        ctx[result.status][self.code] = self.reason
        return result


@register_rule
class RuleToReturnApproved1(Rule):
    def __init__(self):
        self.code = "APPRV_1"
        self.reason = "approved test for rule codes 1"

    def apply(self, app, ctx) -> RuleResult:
        result = RuleResult(RuleStatus.APPROVE, self.code)
        ctx[result.status][self.code] = self.reason
        return result


@register_rule
class RuleToReturnApproved2(Rule):
    def __init__(self):
        self.code = "APPRV_2"
        self.reason = "approved test for rule codes 2"

    def apply(self, app, ctx) -> RuleResult:
        result = RuleResult(RuleStatus.APPROVE, self.code)
        ctx[result.status][self.code] = self.reason
        return result


@register_rule
class RuleToDecline(Rule):
    def __init__(self):
        self.code = "DECLINE"
        self.reason = "declined test for rule codes 2"

    def apply(self, app, ctx) -> RuleResult:
        result = RuleResult(RuleStatus.DECLINE, self.code)
        ctx[result.status][self.code] = self.reason
        return result