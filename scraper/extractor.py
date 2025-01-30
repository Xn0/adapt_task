import requests

from typing import NoReturn, Any
from bs4 import BeautifulSoup

from carriers.models import ParserConfig, FieldConfig, DataConfig

from .models import ResultStatus, ResultModel


class Extractor:
    def __init__(
        self,
        task: dict,
        config: ParserConfig,
        tries_limit: int = 10,
    ):
        self.config: ParserConfig = config
        self.tries = 0
        self.tries_limit = tries_limit
        self.errors = []
        self.status = ResultStatus.pending.value
        self.data = {}
        self.carrier_id = task.get('carrier')
        task.pop('carrier', None)
        self.arguments = task
        self.parsed_urls = []
        self.current_url = self.build_url(
            config.url_template, page=self.config.start_page, **self.arguments)
        self.current_page = config.start_page

    @staticmethod
    def build_url(url_template: str, **kwargs) -> str:
        """
        Replaces placeholders in URL template with actual values
        explect url_template like this: https://site.com/<userId>/page/<page>
        """
        for k, v in kwargs.items():
            url_template = url_template.replace(f'<{k}>', str(v))
        return url_template

    def _make_result(self) -> ResultModel:
        return ResultModel(
            status=self.status,
            carrier=self.carrier_id,
            arguments=self.arguments,
            urls=self.parsed_urls,
            errors=self.errors,
            data=self.data,
        )

    @staticmethod
    def _get_request(url: str) -> requests.Response | NoReturn:
        response = requests.get(url)
        print(f'request {url=}, response code={response.status_code}')
        # TODO other http errors handling
        if response.status_code == 429:
            raise requests.HTTPError('429')

        return response

    def run(self) -> ResultModel:
        # Handle pagination and can scrape multiple pages
        response = self._get_request(self.current_url)
        self.parsed_urls.append(self.current_url)

        if (self.config.multipage
                and response.status_code == 404
                and self.current_page > self.config.start_page):
            # previous page was the last one
            # remove current url from list of parsed urls
            self.parsed_urls.pop()
            self.status = ResultStatus.done.value
            return self._make_result()

        elif response.status_code != 200:
            if self.tries >= self.tries_limit:
                self.errors.append(f'url: error {response.status_code}')
                self.status = ResultStatus.error.value
                return self._make_result()
            else:
                self.tries += 1

        self._scrape_html(response.text)

        if self.config.multipage:
            # last page not reached yet
            self.current_page += 1
            self.current_url = self.build_url(
                self.config.url_template, page=self.current_page, **self.arguments)
        else:
            self.status = ResultStatus.done.value

        return self._make_result()

    def _scrape_html(self, html_text: str) -> None:
        html = BeautifulSoup(html_text, 'html.parser')

        for data_conf in self.config.data:
            if data_conf.array:
                self._scrape_array_fields(data_conf, html)
            else:
                self._scrape_fields(data_conf, html)

    def _scrape_fields(self, data_conf: DataConfig, html: BeautifulSoup) -> None:
        if self.current_page != self.config.start_page:
            # to not scrape the same date again
            return

        self.data[data_conf.name] = {}

        if data_conf.container_selector:
            html = data_conf.container_selector.select(html)

        for field_conf in data_conf.fields:
            err, data = self._scrape_field(html, field_conf)
            if err:
                self.errors.append({f'{data_conf.name}.{field_conf.name}': err})

            self.data[data_conf.name][field_conf.name] = data

    def _scrape_array_fields(self, data_conf: DataConfig, html: BeautifulSoup) -> None:
        self.data[data_conf.name] = self.data.get(data_conf.name, [])

        if data_conf.container_selector:
            html = data_conf.container_selector.select(html)

        for item in html:
            data = {}
            for field_conf in data_conf.fields:
                err, value = self._scrape_field(item, field_conf)
                if err:
                    self.errors.append({f'{data_conf.name}.{field_conf.name}': err})

                data[field_conf.name] = value

            self.data[data_conf.name].append(data)

    @staticmethod
    def _scrape_field(html: BeautifulSoup, field_config: FieldConfig) -> (list[str], Any):
        errors = []
        element = field_config.selector.select(html) if field_config.selector else html
        data = field_config.extractor.extract(element)
        for validator in field_config.validators:
            err = validator.validate(data)
            if err:
                errors.append(err)

        converted_data = field_config.converter.convert(data) if field_config.converter else data

        return errors, converted_data
