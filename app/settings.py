class Settings:
    AUDIT_FILE = "events.jsonl"
    DB_FILE = "dbfile.jsonl"

Config = Settings 

import logging
logging.basicConfig(level=logging.INFO)
