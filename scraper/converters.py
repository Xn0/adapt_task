from typing import Any
from abc import ABC, abstractmethod


class BaseConverter(ABC):
    """
    Abstract base class for value convertion
    """
    @abstractmethod
    def convert(self, value: str) -> Any:
        pass
