from typing import Callable
from abc import ABC, abstractmethod

from bs4 import BeautifulSoup


class BaseElementSelector(ABC):
    """
    Abstract base class for element selector
    """
    @abstractmethod
    def select(self, html: BeautifulSoup) -> BeautifulSoup:
        pass


class CSSSingleSelector(BaseElementSelector):
    def __init__(self, css_selector: str):
        self.css_selector = css_selector

    def select(self, html: BeautifulSoup) -> BeautifulSoup:
        return html.css.select_one(self.css_selector)


class CSSMultiSelector(BaseElementSelector):
    def __init__(self, css_selector: str):
        self.css_selector = css_selector

    def select(self, html: BeautifulSoup) -> BeautifulSoup:
        return html.css.select(self.css_selector)


class CSSNextSiblingSelector(BaseElementSelector):
    def select(self, html: BeautifulSoup) -> BeautifulSoup:
        return html.next_sibling


class CustomSelector(BaseElementSelector):
    def __init__(self, select_method: Callable):
        self.select_method = select_method

    def select(self, html: BeautifulSoup) -> BeautifulSoup:
        return self.select_method(html)
