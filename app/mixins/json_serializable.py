from __future__ import annotations

import json

from datetime import datetime
from decimal import Decimal

from pygments.lexers import data


class JsonSerializableMixin: 

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def to_dict(self):
        data = dict() 
        for key, value in self.__dict__.items():
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
        b4_created_at = self.created_at
        b4_validated_at = self.validated_at
        b4_updated_at = self.updated_at
        j = json.dumps(self.to_dict(), default=str)
        d = json.loads(j)
        # assert d.get("created_at") == b4_created_at
        # assert d.get("validated_at") == b4_validated_at
        # assert d.get("updated_at") == b4_updated_at
        return j

    @classmethod
    def from_dict(cls, data): 
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
        return cls(**processed)
    
    @classmethod
    def from_json(cls, s): 
        return cls.from_dict(json.loads(s))

    def copy(self):
        d = self.to_dict()
        print("created_at dict", d.get("created_at"))
        print("validated_at dict", d.get("validated_at"))
        obj = self.__class__.from_dict(d)
        print("created_at obj", obj.created_at)
        print("validated_at obj", obj.validated_at)
        return obj