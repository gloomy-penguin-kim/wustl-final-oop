from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any 


class Wrapper(ABC): 
    
    @abstractmethod 
    def register(self, item: Any) -> None:...

    @abstractmethod 
    def new(self) -> Any:... 

    @abstractmethod
    def _add_item(self, item: Any) -> None:...

    @abstractmethod
    def get(self, id: str) -> Any:...