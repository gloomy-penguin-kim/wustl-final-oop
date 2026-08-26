import json
import os
from json import JSONDecodeError

from app.audit import HashChain, EmitEvent
from app.domain import domain_registry
from app.domain.base_entity import BaseEntity
from app.domain.domain_registry import register_domain
from app.persistence import JsonCrud
from app.repository.domain_repo import Repository
from app.settings import Config
import pytest

@register_domain
class TestClass(BaseEntity):
    __test__ = False
    def __init__(self, data: dict, *args, **kwargs):
        self._data = data
        super(TestClass, self).__init__(*args, **kwargs)

    @property
    def data(self):
        return self._data
    @data.setter
    def data(self, value):
        self._data = value

    def __repr__(self):
        return f"TestClass(id={self.id}, data={self.data})"


def check_file_for_string(id: str):
    if not os.path.exists("tests/output/test_persistence.jsonl"):
        return None
    with open("tests/output/test_persistence.jsonl", "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if id in line:
                return line
        return None

def test_persist_events(clear_files):
    hc, repo = clear_files()
    arr = []
    for i in range(20):
        t = TestClass(id="test" + str(i), type="TestClass", hash_chain=hc, data={"value": i})
        repo.save(t)
        arr.append(t)

    repo.delete("test" + str(6))
    with pytest.raises(Exception):
        repo.get("test" + str(6))

    if check_file_for_string("test" + str(6)):
        raise AssertionError("This should not raise an error")

    repo.delete("test" + str(12))
    with pytest.raises(Exception):
        repo.get("test" + str(12))

    if check_file_for_string("test" + str(12)):
        raise AssertionError("This should not raise an error")

    t = arr[0]
    t.data = { "value": 123 }
    repo.save(t)
    tt = repo.get(t.id)
    assert tt.data == t.data
    assert tt.data["value"] == 123
    line = check_file_for_string("test" + str(0))
    if "123" not in line:
        raise AssertionError("This should not raise an error")