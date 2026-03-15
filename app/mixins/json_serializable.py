from __future__ import annotations

import json
from datetime import datetime
from decimal import Decimal 


class JsonSerializableMixin:
    """
    Generic JSON serialization mixin.
    Works for most simple domain objects.
    """

    def to_dict(self):
        data = {}

        for key, value in self.__dict__.items(): 

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
        return json.dumps(self.to_dict(), sort_keys=True)

    @classmethod
    def from_dict(cls, data):

        processed = {}

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