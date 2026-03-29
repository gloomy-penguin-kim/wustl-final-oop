class Settings:
    EVENTS_FILE = "events.jsonl"
    AUDIT_FILE = "audit.jsonl"
Config = Settings()

import logging
logging.basicConfig(level=logging.INFO)
