from __future__ import annotations

from app.audit.hash_chain import HashChain

class AuditTrail:

    def __init__(self, sink):
        self.chain = HashChain()
        self.sink = sink

    def emit(self, event: dict):

        record = self.chain.append(event)

        self.sink.emit(record)