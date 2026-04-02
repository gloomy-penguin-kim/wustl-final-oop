from __future__ import annotations

import os
from collections import defaultdict
import json
from datetime import datetime, UTC
from json import JSONDecodeError
from pathlib import Path
from typing import Any, Dict
import logging

from app.audit import EmitEvent
from app.persistence.utility import remove_line_from_large_file
from app.settings import Config

class DuplicateIDError(Exception):
    pass
class InvalidApplicationError(Exception):
    pass


class JsonCrud:
    filename = Config.PERSISTENCE_FILE

    def __init__(self, filename: str = None, *args, **kwargs):
        if self.filename: Config.PERSISTENCE_FILE = filename
        self.filename = Config.PERSISTENCE_FILE

    def save_to_file(self, type: str = None):
        self.delete_from_file_wo_emit()

        with open(JsonCrud.filename, "a", encoding="utf-8") as f:
            record = {
                "type": type or self.type,
                "date": datetime.now(UTC),
                "id": self.id,
                "data": self.to_dict(),
            }
            json.dump(record, f, default=str)
            f.write("\n")

        EmitEvent.emit(event={
            "event": self.type + " Saved",
            "date": datetime.now(UTC),
            "data": str(self),
            "id": self.id
        })

    def update_file(self):
        self.save_to_file()

    def delete_from_file_wo_emit(self) -> bool:
        def to_remove(line):
            if line.strip():
                try:
                    data = json.loads(line)
                    return (data.get("type") == self.__class__.__name__ and
                            data.get("id") == self.id)
                except JSONDecodeError:
                    print(f"JSONDecodeError: {line}")
                    pass
            return None
        return remove_line_from_large_file(JsonCrud.filename, to_remove)

    @classmethod
    def existing_id(cls, id: str, type: str = None) -> bool:
        if not os.path.exists(JsonCrud.filename):
            return False
        class_type = type or cls.__name__
        with open(JsonCrud.filename, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    try:
                        data = json.loads(line)
                        if data.get("type") == class_type and data.get("id") == id:
                            return True
                    except JSONDecodeError as e:
                        print(f"JSONDecodeError: {e}")
                        pass
            return False

    @classmethod
    def load_from_file(cls, id: str):
        if not os.path.exists(JsonCrud.filename):
            return None
        with (open(JsonCrud.filename, "r", encoding="utf-8") as f):
            for line in f:
                try:
                    data = json.loads(line)
                    if (data.get("type") == cls.__name__ and
                        data.get("id") == id):
                        return cls.from_dict(data.get("data"))
                except:
                    pass
            return None

    @classmethod
    def delete_from_file_by_id(cls, id: str, type: str = None):
        type = type or cls.__name__
        if cls.delete_from_file_by_id_wo_emit(id, type):
            EmitEvent.emit(event={
                "event": type + " Deleted",
                "date": datetime.now(UTC),
                "id": id
            })

    @classmethod
    def delete_from_file_by_id_wo_emit(cls, id: str, type: str = None) -> bool:
        type = type or cls.__name__

        def to_remove(line):
            if line.strip():
                try:
                    data = json.loads(line)
                    return (data.get("type") == type and
                            data.get("id") == id)
                except JSONDecodeError:
                    print(f"JSONDecodeError: {line}")
                    pass
            return None
        return remove_line_from_large_file(JsonCrud.filename, to_remove)

    @classmethod
    def duplicate_check(cls, id: str, type: str = None):
        if id:
            if cls.existing_id(id, type):
                raise DuplicateIDError(f"ID \"{id}\" already exists in Persistence File: {cls.filename}")

    @classmethod
    def clear(cls):
        print(f"clearing file... {cls.filename}")
        with open(cls.filename, "w", encoding="utf-8") as f:
            f.write("\n")
