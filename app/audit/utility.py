import json 
import hashlib 

def hash_event(event: dict, prev_hash: str) -> str: 
    prev_hash = "" if not prev_hash else str(prev_hash) 
    payload = json.dumps(event, default=str) 
    return hashlib.sha256((payload + prev_hash).encode()).hexdigest()