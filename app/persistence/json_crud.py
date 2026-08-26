from __future__ import annotations

import os
import json
from datetime import datetime, UTC
from json import JSONDecodeError

from app.audit import EmitEvent
from app.persistence.utility import remove_line_from_large_file
from app.settings import Config

from app.audit.event_sink import emit


class JsonCrud:
    filename = Config.PERSISTENCE_FILE

    def __init__(self, filename: str = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if filename: JsonCrud.filename = filename


    def save_to_file(self, item):
        id = item.id
        self.delete_from_file_by_id(id)
        with open(JsonCrud.filename, "a", encoding="utf-8") as f:
            record = {
                "type": item.type,
                "id": item.id,
                "date": datetime.now(UTC),
                "data": item.to_dict(),
            }
            json.dump(record, f, default=str)
            f.write("\n")


    def load_from_file(self, id: str):
        if not os.path.exists(self.__class__.filename):
            return None
        with open(self.__class__.filename, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    try:
                        data = json.loads(line)
                        if data.get("id") == id:
                            return data
                    except JSONDecodeError as e:
                        print(f"JSONDecodeError (2): {e}, {line}")
                        pass
            return None

    def delete_from_file_by_id(self, id: str) -> bool:
        def to_remove(line):
            if line.strip():
                try:
                    data = json.loads(line)
                    return data.get("id") == id
                except JSONDecodeError as e:
                    print(f"JSONDecodeError (3): {e}")
                    pass
            return None
        return remove_line_from_large_file(self.__class__.filename, to_remove)

    def clear(self):
        emit.emit(event={
            "event": "Clearing persistence file",
            "id": JsonCrud.filename,
            "date": datetime.now(UTC),
        })
        with open(JsonCrud.filename, "w", encoding="utf-8") as f:
            f.write("")
