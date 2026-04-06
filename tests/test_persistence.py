from app.audit import HashChain, EmitEvent
from app.domain.base_entity import BaseEntity
from app.persistence import JsonStore, JsonCrud
from app.settings import Config
import pytest

class TestClass(BaseEntity):
    def __init__(self, data: dict, *args, **kwargs):
        super(TestClass, self).__init__(*args, **kwargs)
        self._data = data
        self.init(**kwargs)
        self.save()
    @property
    def data(self):
        return self._data
    @data.setter
    def data(self, value):
        self._data = value
    def __repr__(self):
        return f"TestClass(id={self.id}, data={self.data})"


def test_persist_events():
    hc = HashChain("tests/output/test_audit.jsonl")
    hc.clear()
    ee = EmitEvent("tests/output/test_events.jsonl")
    ee.clear()
    jc = JsonCrud("tests/output/test_persistence.jsonl")
    jc.clear()

    arr = []
    for i in range(20):
        t = TestClass(id="test" + str(i), type="TestClass", data={"value": i})
        arr.append(t)

    TestClass.delete("test" + str(6))
    with pytest.raises(Exception):
        TestClass.load_from_file("test" + str(6))

    TestClass.delete("test" + str(12))
    with pytest.raises(Exception):
        TestClass.load_from_file("test" + str(12))

    t = arr[0]
    t.data = { "value": 123 }
    t.save()
    tt = TestClass.load_from_file(t.id)
    assert tt.data == t.data
    assert tt.data["value"] == 123
