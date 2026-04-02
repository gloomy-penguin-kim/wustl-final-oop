from app.audit.event_sink import EventSink, FileEventSink, InMemoryEventSink, PrintEventSink
from app.audit.hash_chain import HashChain
from app.domain import Decision 
from app.domain.base import BaseEntity
from app.mixins.hash_chain_mixin import HashChainAuditMixin
from app.mixins.json_serializable import JsonSerializableMixin
from app.mixins.validate_decision import ValidatableMixin
from app.rules import Status
from app.engine import Loans, Wrapper
from app.audit import EmitEvent
from app.persistence import JsonStore
from abc import ABC
from app.settings import Config

Config.AUDIT_FILE = "tests/output/test_audit.jsonl"
Config.EVENTS_FILE_FILE = "tests/output/test_events.jsonl"



def test_decision_mro1():
 
    assert Decision.__mro__[0] is Decision
    assert Decision.__mro__[1] is ValidatableMixin
    assert Decision.__mro__[2] is JsonSerializableMixin 
    assert Decision.__mro__[3] is BaseEntity
    assert Decision.__mro__[4] is ABC

 
  
def test_mro_loans():   
    print(Loans.__mro__)
    assert Loans.__mro__[0] is Loans
    assert Loans.__mro__[1] is Wrapper
    assert Loans.__mro__[2] is JsonStore
    assert Loans.__mro__[3] is EmitEvent
    assert Loans.__mro__[4] is InMemoryEventSink
    assert Loans.__mro__[5] is FileEventSink
    assert Loans.__mro__[6] is PrintEventSink
    assert Loans.__mro__[7] is EventSink
    assert Loans.__mro__[8] is ABC
    assert Loans.__mro__[9] is HashChain
    assert Loans.__mro__[10] is HashChainAuditMixin 
    assert Loans.__mro__[11] is object 