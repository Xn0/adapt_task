from typing import Callable
from abc import ABC, abstractmethod


class BaseValidator(ABC):
    """
    Abstract base class for data validation
    """
    @abstractmethod
    def validate(self, value: str) -> str:
        pass
