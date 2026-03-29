import json 
import hashlib
import logging
<<<<<<< HEAD
=======

>>>>>>> origin/main
from app.settings import Config 
 

def hash_event(event: dict, prev_hash: str) -> str:
    payload = {
        "event": event,
        "prev_hash": prev_hash
    }
    canonical = json.dumps(payload, sort_keys=True, ensure_ascii=False, indent=None)
    return hashlib.sha256(canonical.encode()).hexdigest()


def get_last_hash_from_file(filename: str):
    count = 0 
    last_hash = None
    try:   
        with open(filename, "r", encoding="utf-8") as f:
            for line in f: 
                if len(line.strip()) == 0: continue 
                count += 1 
                try: 
                    event = json.loads(line)
                    if event["type"] == "emit" and "hash_self" in event: 
                        last_hash = event["hash_self"] 
                        count += 1 
                except:
                    logging.warning(f"could not load line: {line}")
                    pass
    except FileNotFoundError:
        logging.warning("Audit file not found, starting new hash chain.")
        pass
    if count > 1000: 
        logging.warning(f"Audit file has {count} records, which may impact performance: {filename}")
    return last_hash