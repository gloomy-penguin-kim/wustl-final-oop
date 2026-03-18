from __future__ import annotations

from collections import defaultdict
import json
from pathlib import Path
from typing import Any, Dict
from settings import Config

from app.domain.application import LoanApplication

class JsonStore:

    def __init__(self):
        self.filename = Config.DB_FILE 

    def append(self, record): 
        with open(self.filename, "a", encoding="utf-8") as f:
            json.dump(record, f, sort_keys=True)
            f.write("\n")

    def save(self, record): 
        with open(self.filename, "a", encoding="utf-8") as f:
            json.dump(record, f, sort_keys=True)
            f.write("\n")

    def update_file(self, items: dict): 
        with open(self.filename, "w", encoding="utf-8") as f: 
            for _,item in items.items():  
                # try: 
                    json.dump(item, f, sort_keys=True)
                    f.write("\n") 
                    print("item saved:", item)
                # except:
                #     print("could not save item:", item)
                #     pass 
                # print("")

    def clear_file(self): 
        print(f"clearing file... {self.filename}")
        with open(self.filename, "w", encoding="utf-8") as f: 
            f.write("\n")  

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
                        print(f"could not load line: {line}")
                        pass  
        return records

    def load_by_type(self) -> dict: 
        r = {}  
        for record in self.load_all():   
            if "type" in record and "id" in record and "data" in record and record["type"] == self.__class__.__name__: 
                r[record["id"]] = record # cls.from_dict()   
        return r 
     
    
    # def load_application(self, application_id: str): 
    #     for record in self.load_all(): 
    #         if record["type"] == "application" and record["id"] == application_id: 
    #             return LoanApplication.from_dict(record["data"]) 
    #     raise ValueError(f"Application not found: {application_id}")
    
    def load_events(self, application_id: str): 
        events = [] 
        for record in self.load_all(): 
            if record["type"] == "audit" and record["id"] == application_id:
                events.append(record) 
        return events
    
    def load_policy(self, version: str): 
        for record in self.load_all(): 
            if "type" in record and record["type"] == "policy" and record["id"] == version: 
                return record["data"] 
        raise ValueError(f"Policy not found: {version}")
    
    def load_policies(self) -> Dict: 
        d = {} 
        for record in self.load_all(): 
            if "type" in record and record["type"] == "policy": 
                d[record["id"]] = record["data"]
        return d 