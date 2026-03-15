from __future__ import annotations

from audit.hash_chain import HashChain

class AuditTrail:

    def __init__(self, sink):
        self.chain = HashChain()
        self.sink = sink

    def emit(self, event: dict):

        record = self.chain.append(event, event["application_id"])

        self.sink.emit(record)