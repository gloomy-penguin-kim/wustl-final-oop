from models import Event 

class HashChainedAuditMixin(): 
    def audit(self, events: list[Event]):
        prev = None 
        for event in events: 
            if prev and prev != event.hash_prev:
                raise KeyError("Event chain does not match")
            prev = event.hash_self