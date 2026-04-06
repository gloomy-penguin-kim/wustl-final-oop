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
        super().__init__(*args, **kwargs)
        if filename: JsonCrud.filename = filename

    @classmethod
    def delete(cls, id: str, type: str = None):
        type = type or cls.__name__
        cls.delete_from_file_by_id(id, type)

    def save(self, type: str = None, old_id: str = None):
        id = old_id or self.id
        type = type or self.__class__.__name__

        JsonCrud.delete_from_file_by_id_wo_emit(id, type)

        with open(JsonCrud.filename, "a", encoding="utf-8") as f:
            record = {
                "type": type or self.type,
                "id": self.id,
                "date": datetime.now(UTC),
                "data": self.to_dict(),
            }

            json.dump(record, f, default=str)
            f.write("\n")

        EmitEvent.emit(event={
            "event": self.type + " Saved",
            "id": self.id,
            "date": datetime.now(UTC),
            "data": str(self),
        })

    @classmethod
    def existing_id(cls, id: str, type: str = None) -> bool:
        if not os.path.exists(cls.filename):
            return False
        class_type = type or cls.__name__
        with open(cls.filename, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    try:
                        data = json.loads(line)
                        if (data.get("type") == class_type and
                            data.get("id") == id):
                            return True
                    except JSONDecodeError as e:
                        print(f"JSONDecodeError (1): {e}, {line}")
                        pass
            return False

    @classmethod
    def load_from_file(cls, id: str):
        if not os.path.exists(cls.filename):
            return None
        with open(cls.filename, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    try:
                        data = json.loads(line)
                        if (data.get("type") == cls.__name__ and
                            data.get("id") == id):
                            return cls.from_dict(data.get("data"))
                    except JSONDecodeError as e:
                        print(f"JSONDecodeError (2): {e}, {line}")
                        pass
            raise ValueError(f"Type '{cls.__name__}', ID '{id}' were not found in persistence file: {cls.filename}")

    @classmethod
    def delete_from_file_by_id(cls, id: str, type: str = None):
        type = type or cls.__name__
        if cls.delete_from_file_by_id_wo_emit(id, type):
            EmitEvent.emit(event={
                "event": type + " Deleted",
                "id": id,
                "date": datetime.now(UTC),
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
                except JSONDecodeError as e:
                    print(f"JSONDecodeError (3): {e}")
                    pass
            return None
        return remove_line_from_large_file(cls.filename, to_remove)

    @classmethod
    def duplicate_check_in_file(cls, id: str, type: str = None):
        type = type or cls.__name__
        if cls.existing_id(id, type):
            raise DuplicateIDError(f"ID \"{id}\" already exists in Persistence File: {cls.filename}")

    @staticmethod
    def clear():
        EmitEvent.emit(event={
            "event": "Clearing persistence file",
            "id": JsonCrud.filename,
            "date": datetime.now(UTC),
        })
        with open(JsonCrud.filename, "w", encoding="utf-8") as f:
            f.write("\n")
