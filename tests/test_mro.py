from app.domain.decision import Decision
from app.mixins.reason_codes import ReasonCodeMixin
from app.mixins.validatable import ValidatableMixin
from app.rules.rule_result import Status


def test_decision_mro1():

    mro = Decision.__mro__

    assert ReasonCodeMixin in mro
    assert ValidatableMixin in mro

def test_mro_validation_chain():

    d = Decision(
        status=Status.DECLINE,
        reason_codes=["B", "A", "A"],
        policy_version="v1"
    )

    assert d.reason_codes == ("A", "B")    

def test_decision_mro2():

    assert Decision.__mro__[1] is ReasonCodeMixin
    assert Decision.__mro__[2] is ValidatableMixin    