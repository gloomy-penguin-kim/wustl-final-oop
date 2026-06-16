from __future__ import annotations

import json

from datetime import datetime
from decimal import Decimal

from pygments.lexers import data

from app.audit import HashChain


class JsonSerializableMixin: 

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def to_dict(self):
        data = dict() 
        for key, value in self.__dict__.items():
            if key == '_hash_chain': continue
            if key[0] == '_': key = key[1:]
            if isinstance(value, Decimal):
                data[key] = str(value) 
            elif isinstance(value, datetime):
                data[key] = value.isoformat() 
            elif hasattr(value, "to_dict"):
                data[key] = value.to_dict()  
            else:
                data[key] = value
        return data
    
    def to_json(self):
        return json.dumps(self.to_dict(), default=str)

    @classmethod
    def from_dict(cls, hash_chain: HashChain, data: dict):
        processed = dict()  
        for key, value in data.items():
            if isinstance(value, str):
                try:
                    processed[key] = Decimal(value)
                    continue
                except:
                    pass 
                try:
                    processed[key] = datetime.fromisoformat(value)
                    continue
                except:
                    pass

            processed[key] = value

        processed["hash_chain"] = hash_chain
        return cls(**processed)
    
    @classmethod
    def from_json(cls, hash_chain: HashChain, s: str):
        return cls.from_dict(hash_chain, json.loads(s))

    def copy(self):
        d = self.to_dict()
        obj = self.__class__.from_dict(self.hash_chain, d)
        return obj
