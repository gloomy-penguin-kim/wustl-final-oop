from abc import ABC, abstractmethod
import csv
from decimal import Decimal
import io
import json
from typing import Any


class SerializableMixin(ABC):
    """A mixin to add serialization behavior to any class."""
    def to_dict(self) -> dict:
        """Returns a dictionary representation of the object's attributes."""
        # Check if the class uses __slots__, otherwise use __dict__
        d = {}  
        if hasattr(self, "__slots__"):
            d = dict() 
            for name in self.__slots__: 
                d[name] = getattr(self, name)   
                if isinstance(d[name], Decimal):
                    d[name] = float(d[name]) 
                if isinstance(d[name], SerializableMixin):
                    d[name] = d[name].to_dict()   
        return d 
    
    def to_json(self) -> str:  
        return json.dumps(self.to_dict(), default=str) 
    
    def to_csv(self):
        buf = io.StringIO()
        to_dict = self.to_dict() 
        writer = csv.DictWriter(buf, fieldnames=to_dict.keys())
        writer.writeheader()
        writer.writerows(to_dict)
        return buf.getvalue()
    
    @abstractmethod
    def from_dict(self, d: dict) -> Any: ... 
     
    def from_json(self, s: str):  
        return self.from_dict(json.loads(s))
    
             