from app.persistence import JsonStore 
from app.settings import Config

Config.AUDIT_FILE = "tests/output/emit_events.jsonl"

def test_persist_events():
    store = JsonStore("tests/output/test_persistence.jsonl")
    store.clear_file() 

    events = {
        "1": {"type": "test_item", "id": "1", "data": {"value": 123}},
        "2": {"type": "test_item", "id": "2", "data": {"value": 456}},
        "3": {"type": "test_item", "id": "3", "data": {"value": 789}},
        "4": {"type": "test_item", "id": "4", "data": {"value": 101112}},
        "5": {"type": "test_item", "id": "5", "data": {"value": 13141516}},
        "6": {"type": "test_item", "id": "6", "data": {"value": 171819}},
    }
    for key, event in events.items():
        store.save(event)
    
    loaded_events = store.load_all()

    assert len(loaded_events) == len(events)

    for eKey, le in zip(events.keys(), loaded_events):
        assert events[eKey]["id"] == le["id"]
        assert events[eKey]["data"] == le["data"]
    
    del events["3"]
    assert "3" not in events 

    store.update_file(events) 
    loaded_events = store.load_all()

    for eKey, le in zip(events.keys(), loaded_events):
        assert events[eKey]["id"] == le["id"]
        assert events[eKey]["data"] == le["data"]

    store.clear_file() 
    loaded_events = store.load_all()
    assert len(loaded_events) == 0

def test_persist_events_with_invalid_json():
    store = JsonStore("tests/output/test_persistence.jsonl")
    store.clear_file() 

    events = {
        "1": {"type": "test_item", "id": "1", "data": {"value": 123}},
        "2": {"type": "test_item", "id": "2", "data": {"value": 456}},
        "3": {"type": "test_item", "id": "3", "data": {"value": 789}},
        "4": {"type": "test_item", "id": "4", "data": {"value": 101112}},
        "5": {"type": "test_item", "id": "5", "data": {"value": 13141516}},
        "6": {"type": "test_item", "id": "6", "data": {"value": 171819}},
    }
    for key, event in events.items():
        store.save(event)
    
    with open(store.filename, "a", encoding="utf-8") as f:
        f.write("this is not valid json\n")
    
    loaded_events = store.load_all()

    assert len(loaded_events) == len(events)

    for eKey, le in zip(events.keys(), loaded_events):
        assert events[eKey]["id"] == le["id"]
        assert events[eKey]["data"] == le["data"]
    
    store.clear_file()
    
def test_load_by_type():
    store = JsonStore("tests/output/test_persistence.jsonl")
    store.clear_file()

    events = {
        "1": {"type": "JsonStore", "id": "1", "data": {"value": 123}},
        "2": {"type": "JsonStore", "id": "2", "data": {"value": 456}},
        "3": {"type": "other_item", "id": "3", "data": {"value": 789}},
        "4": {"type": "JsonStore", "id": "4", "data": {"value": 101112}},
        "5": {"type": "other_item", "id": "5", "data": {"value": 13141516}},
        "6": {"type": "JsonStore", "id": "6", "data": {"value": 171819}},
    }
    for key, event in events.items():
        store.save(event)
    
    loaded_by_type = store.load_by_type()

    assert len(loaded_by_type) == 4

    for key, item in loaded_by_type.items():
        assert item["type"] == "JsonStore"
    
    store.clear_file() 

