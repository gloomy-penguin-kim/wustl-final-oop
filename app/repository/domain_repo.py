from datetime import datetime, UTC

from app.audit import EmitEvent
from app.domain.base import Base
from app.domain.base_entity import BaseEntity
from app.persistence import JsonCrud

from typing import Protocol, Any


class DomainRepository(Protocol):
    def get(self, id: str, type: str) -> BaseEntity: ...
    def add(self, item: BaseEntity) -> None: ...
    def save(self, item: BaseEntity) -> None: ...
    def delete(self, item: BaseEntity) -> None: ...

class Repository(JsonCrud, EmitEvent, DomainRepository):
    def __init__(self, filename: str = None):
        super().__init__(filename=filename)

    def get(self, id: str, type: str) -> Any:
        return self.load_from_file(id, type)

    def add(self, item: BaseEntity):
        if self.existing(id=item.id, type=item.type):
            raise Exception(f"duplicate id: {item.type}, {item.id}")
        EmitEvent.emit(event={
            "event": item.type + " Added to Repository",
            "id": item.id,
            "date": datetime.now(UTC),
            "data": str(item),
        })
        return self.save_to_file(item)

    def save(self, item: BaseEntity, old_id: str = None):
        EmitEvent.emit(event={
            "event": item.type + " Updated in Repository",
            "id": item.id,
            "date": datetime.now(UTC),
            "data": str(item),
        })
        return self.save_to_file(item, old_id)

    def delete(self, item: BaseEntity):
        EmitEvent.emit(event={
            "event": item.type + " Deleted from Repository",
            "id": item.id,
            "date": datetime.now(UTC),
            "data": str(item),
        })
        return self.delete_from_file_by_id(item.id, item.type)

    def existing(self, id: str, type: str):
        return self.existing_id(id, type)