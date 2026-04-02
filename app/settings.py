from dataclasses import dataclass


@dataclass
class Settings:
    EVENTS_FILE = "events.jsonl"
    AUDIT_FILE = "audit.jsonl"
    PERSISTENCE_FILE = "persistence.jsonl"

Config = Settings()
