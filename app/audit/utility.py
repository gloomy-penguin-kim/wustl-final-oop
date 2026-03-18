import json 
import hashlib 
from app.settings import Config 

def hash_event(event: dict, prev_hash: str) -> str: 
    prev_hash = "" if not prev_hash else str(prev_hash) 
    payload = json.dumps(event, default=str) 
    return hashlib.sha256((payload + prev_hash).encode()).hexdigest()


def get_last_hash_from_file():
    count = 0 
    last_hash = None
    try:   
        with open(Config.AUDIT_FILE, "r", encoding="utf-8") as f:
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
        logging.warning(f"Audit file has {count} records, which may impact performance.")
    return last_hash