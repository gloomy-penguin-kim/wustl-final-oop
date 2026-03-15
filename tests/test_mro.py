from app.domain.decision import Decision
from app.mixins.reason_codes import ReasonCodeMixin
from app.mixins.validatable import ValidatableMixin


def test_decision_mro():

    mro = Decision.__mro__

    assert ReasonCodeMixin in mro
    assert ValidatableMixin in mro

def test_mro_validation_chain():

    d = Decision(
        status="DECLINE",
        reason_codes=["B", "A", "A"],
        policy_version="v1"
    )

    assert d.reason_codes == ("A", "B")    

def test_decision_mro():

    assert Decision.__mro__[1] is ReasonCodeMixin
    assert Decision.__mro__[2] is ValidatableMixin    