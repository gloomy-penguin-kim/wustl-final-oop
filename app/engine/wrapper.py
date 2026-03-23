from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any 


class Wrapper(ABC):  

    @abstractmethod
    def register(self, *args, **kwargs) -> Any:...

    @abstractmethod
    def new(self, *args, **kwargs) -> Any:...

    @abstractmethod
    def _add_item(self, *args, **kwargs) -> None:...

    @abstractmethod
    def get(self, *args, **kwargs) -> Any:...

    @abstractmethod 
    def delete(self, *args, **kwargs) -> None:... 

    @abstractmethod 
    def clear(self, *args, **kwargs)  -> None:... 