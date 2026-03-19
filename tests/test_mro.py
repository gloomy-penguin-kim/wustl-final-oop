from app.domain import Decision 
from app.mixins.validatable import ValidatableMixin
from app.rules import Status
from app.engine import Loans, Wrapper
from app.audit import FileEventSink, PrintEventSink, AuditEventSink, EmitEvent, EventSink
from app.persistence import JsonStore
from abc import ABC
from app.settings import Config

Config.AUDIT_FILE = "tests/output/emit_events.jsonl"


def test_decision_mro1():

    mro = Decision.__mro__
    assert ValidatableMixin in mro
 

def test_decision_mro2():
    assert Decision.__mro__[1] is ValidatableMixin    


def test_mro_loans():   
    pass
    # assert Loans.__mro__[0] is Loans
    # assert Loans.__mro__[1] is Wrapper
    # assert Loans.__mro__[2] is JsonStore
    # assert Loans.__mro__[3] is EmitEvent
    # assert Loans.__mro__[4] is FileEventSink
    # assert Loans.__mro__[5] is PrintEventSink
    # # assert Loans.__mro__[6] is AuditEventSink
    # # assert Loans.__mro__[6] is EventSink
    # # assert Loans.__mro__[7] is ABC
    # # assert Loans.__mro__[8] is object