from app.audit.event_sink import EventSink, FileEventSink, InMemoryEventSink, PrintEventSink
from app.audit.hash_chain import HashChain
from app.domain import Decision, LoanApplication
from app.domain.base_entity import BaseEntity, Base
from app.mixins.hash_chain_mixin import HashChainAuditMixin
from app.mixins.json_serializable import JsonSerializableMixin
from app.audit import EmitEvent
from app.mixins.normalize_reason_codes import NormalizeReasonCodesMixin
from app.mixins.validate_base import ValidateBaseEntity
from app.mixins.validate_decision import ValidateDecisionMixin
from app.persistence import JsonCrud
from abc import ABC


def test_decision_mro1():
    assert Decision.__mro__[0] is Decision
    assert Decision.__mro__[1] is ValidateDecisionMixin
    assert Decision.__mro__[2] is NormalizeReasonCodesMixin
    assert Decision.__mro__[3] is BaseEntity
    assert Decision.__mro__[4] is ValidateBaseEntity
    assert Decision.__mro__[5] is JsonSerializableMixin
    assert Decision.__mro__[6] is Base
    assert Decision.__mro__[7] is ABC

  
def test_mro_loans():   
    print(EmitEvent.__mro__)
    assert EmitEvent.__mro__[0] is EmitEvent
    assert EmitEvent.__mro__[1] is InMemoryEventSink
    assert EmitEvent.__mro__[2] is FileEventSink
    assert EmitEvent.__mro__[3] is PrintEventSink
    assert EmitEvent.__mro__[4] is EventSink
    assert EmitEvent.__mro__[5] is ABC