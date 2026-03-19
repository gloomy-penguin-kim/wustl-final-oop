from __future__ import annotations

from collections import defaultdict
import json
from pathlib import Path
from typing import Any, Dict
import logging 


class JsonStore:

    def __init__(self, filename: str, **kwargs):
        self.filename = filename 

    def save(self, record): 
        with open(self.filename, "a", encoding="utf-8") as f:
            json.dump(record, f, default=str)
            f.write("\n")

    def update_file(self, items: dict): 
        with open(self.filename, "w", encoding="utf-8") as f: 
            for _,item in items.items():  
                try: 
                    json.dump(item, f, default=str)
                    f.write("\n")  
                except:
                    logging.warning(f"{self.filename} could not save item:", item)
                    pass  

    def clear_file(self): 
        print(f"clearing file... {self.filename}")
        with open(self.filename, "w", encoding="utf-8") as f: 
            f.write("\n")

    def load_one(self, id: str) -> dict | None:
        records = []
        path = Path(self.filename)
        if path.is_file():
            with open(self.filename, "r", encoding="utf-8") as f:
                for line in f:
                    if len(line.strip()) == 0: continue
                    try:
                        item = json.loads(line)
                        if item.get("type") == self.__class__.__name__ and item.get("id") == id:
                            return item
                    except:
                        logging.warning(f"{self.filename} could not load line: {line}")
                        pass
        return None

    def load_all(self): 
        records = [] 
        path = Path(self.filename) 
        if path.is_file(): 
            with open(self.filename, "r", encoding="utf-8") as f:
                for line in f:  
                    if len(line.strip()) == 0: continue 
                    try: 
                        records.append(json.loads(line))
                    except:
                        logging.warning(f"{self.filename} could not load line: {line}")
                        pass  
        return records

    def load_by_type(self) -> dict: 
        r = {}  
        for record in self.load_all():   
            if "type" in record and "id" in record and "data" in record and record["type"] == self.__class__.__name__: 
                r[record["id"]] = record # cls.from_dict()   
        return r 
     
    def count(self) -> int: 
        count = 0 
        path = Path(self.filename) 
        if path.is_file(): 
            with open(self.filename, "r", encoding="utf-8") as f:
                count = sum(1 for line in f)
        return count 