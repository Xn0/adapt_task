import requests
import re

from typing import NoReturn
from abc import ABC, abstractmethod

from bs4 import BeautifulSoup

from .models import ResultModel


class CarrierABC(ABC):
    """
    Base class for all carrier implementations
    """
    @abstractmethod
    def __init__(
        self,
        task: dict,
    ):
        ...

    @abstractmethod
    def run(self) -> ResultModel:
        ...

    @abstractmethod
    def _make_result(self) -> ResultModel:
        ...

    @staticmethod
    def build_url(url_template: str, **kwargs) -> str:
        """
        Replaces placeholders in URL template with actual values
        explect url_template like this: https://site.com/<userId>/page/<page>
        """
        for k, v in kwargs.items():
            url_template = url_template.replace(f'<{k}>', str(v))
        return url_template

    def _scrape_fields(self, html: BeautifulSoup, fields: dict) -> dict:
        # Extracts multiple fields from HTML using provided mapping
        # TODO validation

        data = {}
        for field, props in fields.items():
            data[field] = self._scrape_field(html, props)

        return data

    def _scrape_field(self, html: BeautifulSoup, props: dict) -> str | None:
        if props.get('regex'):
            return self._re_scraper(html, props)
        elif props.get('css_selector'):
            return self._css_scraper(html, props)
        elif props.get('custom_scraper'):
            # return props['custom_scraper']() TODO
            return

    @staticmethod
    def _css_scraper(html: BeautifulSoup, props: dict) -> str | None:
        value = html.css.select_one(props['css_selector'])
        return value.string if value else None

    @staticmethod
    def _re_scraper(html: BeautifulSoup, props: dict) -> str | None:
        value = html.css.select_one(props['css_selector'])
        if not value:
            return

        match = re.search(props['regex'], str(value))
        if match:
            return match.group(0)

    @staticmethod
    def _get_request(url: str) -> requests.Response | NoReturn:
        response = requests.get(url)
        print(f'request {url=}, response code={response.status_code}')
        # TODO other http errors handling
        if response.status_code == 429:
            raise requests.HTTPError('429')

        return response

