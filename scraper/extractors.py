from abc import ABC, abstractmethod
from typing import Callable
from bs4 import BeautifulSoup
import re


class BaseValueExtractor(ABC):
    """
    Abstract base class for value extractors
    """
    @abstractmethod
    def extract(self, element: BeautifulSoup) -> str | None:
        pass


class HTMLValueExtractor(BaseValueExtractor):
    """
    Extracts data using CSS selectors
    """
    def extract(self, html: BeautifulSoup) -> str | None:
        return html.string if html else None


class RegexExtractor(BaseValueExtractor):
    """
    Extracts data using regex patterns
    """
    def __init__(self, regex: str):
        self.regex = regex

    def extract(self, html: BeautifulSoup) -> str | None:
        if not html:
            return None

        match = re.search(self.regex, str(html))
        if match:
            return match.group(0)


class CustomExtractor(BaseValueExtractor):
    """
    Extracts data using provided function
    """
    def __init__(self, extract_method: Callable):
        self.extract_method = extract_method

    def extract(self, html: BeautifulSoup) -> str | None:
        if not html:
            return None

        return self.extract_method(html)
