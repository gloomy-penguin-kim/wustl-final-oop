from datetime import datetime, UTC

from app.audit import EmitEvent, HashChain
from app.domain.base_entity import BaseEntity
from app.domain.domain_registry import DOMAIN_REGISTRY
from app.persistence import JsonCrud

from typing import Protocol, Any, overload

from app.audit.hash_chain import hc
from app.audit.event_sink import emit


class DomainRepository(Protocol):
    def get(self, id: str) -> BaseEntity: ...
    def update(self, item: BaseEntity) -> None: ...
    def save(self, item: BaseEntity) -> None: ...
    def delete(self, item: Any) -> None: ...

class Repository(JsonCrud, DomainRepository):
    def __init__(self, hash_chain: HashChain = None, filename: str = None):
        self._hash_chain = hc if hash_chain is None else hash_chain
        super().__init__(filename=filename)

    def get(self, id: str, hash_chain: HashChain = None) -> Any:
        data = self.load_from_file(id)
        hash_chain = hash_chain or self._hash_chain
        print("repository", hash_chain)
        if not data:
            raise ValueError(f"Item not found: {id}")
        return DOMAIN_REGISTRY[data.get("type")].from_dict(hash_chain, data=data.get("data"))

    def update(self, item: BaseEntity):
        if self.load_from_file(id=item.id):
            raise Exception(f"duplicate id: {item.type}, {item.id}")
        emit.emit(event={
            "event": item.type + " Added to Repository",
            "id": item.id,
            "date": datetime.now(UTC),
            "data": str(item),
        })
        return self.save_to_file(item)

    def save(self, item: BaseEntity):
        emit.emit(event={
            "event": item.type + " Updated in Repository",
            "id": item.id,
            "date": datetime.now(UTC),
            "data": str(item),
        })
        return self.save_to_file(item)

    @overload
    def delete(self, item: BaseEntity): ...
    def delete_by_item(self, item: BaseEntity):
        emit.emit(event={
            "event": item.type + " Deleted from Repository",
            "id": item.id,
            "date": datetime.now(UTC),
            "data": str(item),
        })
        return self.delete_from_file_by_id(item.id)

    @overload
    def delete(self, id: str): ...
    def delete_by_str(self, id: str):
        emit.emit(event={
            "event": "Deleted from Repository",
            "id": id,
            "date": datetime.now(UTC)
        })
        return self.delete_from_file_by_id(id)

    def delete(self, item: Any):
        if isinstance(item, str):
            self.delete_by_str(item)
            return
        self.delete_by_item(item)

    def existing(self, id: str):
        return self.load_from_file(id) is not None

repo = Repository(hash_chain=hc)