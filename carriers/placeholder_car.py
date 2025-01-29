from bs4 import BeautifulSoup

from .carrier import CarrierABC
from .models import ResultStatus, ResultModel

START_PAGE_INDEX = 1
URL_TEMPLATE = 'https://scraping-interview.onrender.com/placeholder_carrier/<customerId>/policies/<page>'
SINGLE_CSS_MAPPING = {
    'agent': {
        'name': {'css_selector': '.agency-details .nice-formatted-kv label[for="name"] + span'},
        'producer_code': {'css_selector': '.agency-details .nice-formatted-kv label[for="producerCode"] + span'},
        'agency_name': {'css_selector': '.agency-details .nice-formatted-kv label[for="agencyName"] + span'},
        'agency_code': {'css_selector': '.agency-details .nice-formatted-kv label[for="agencyCode"] + span'},
    },
    'customer': {
        'id': {'css_selector': '.customer-details', 'regex': r'(?<=Id:<\/label><span>)(.+)(?=<\/span>)'},
        'name': {'css_selector': '.customer-details label[for="name"] + span'},
        'ssn': {'css_selector': '.customer-details', 'regex': r'(?<=SSN:<\/label><span>)\d{9}(?=<\/span>)'},
        'email': {'css_selector': '.customer-details', 'regex': r'(?<=Email:<\/label>)(.+)(?=\n)'},
        'address': {'css_selector': '.customer-details', 'regex': r'(?<=Address: )(.+)(?=<\/div>)'},
    },
}
ARRAY_CSS_MAPPING = {
    'policy': {
        'css_selector': '.policy-info-row',
        'fields': {
            'id': {'css_selector': '.policy-info-row td:nth-child(1)'},
            'premium': {'css_selector': '.policy-info-row td:nth-child(2)', 'validator': {'method': 'TODO', 'kwargs': {'precision': 2}}},
            'status': {'css_selector': '.policy-info-row td:nth-child(3)'},
            'effective_date': {'css_selector': '.policy-info-row td:nth-child(4)', 'validator': {'method': 'TODO', 'kwargs': {'format': '%m/%d/%y'}}},
            'termination_date': {'css_selector': '.policy-info-row td:nth-child(5)', 'validator': {'method': 'TODO', 'kwargs': {'format': '%m/%d/%y'}}},
            'last_payment_date': {'custom_scraper': 'TODO', 'validator': {'method': 'TODO', 'kwargs': {'format': '%m/%d/%y'}}},
            'commission_rate': {'custom_scraper': 'TODO'},
            'number_of_insureds': {'custom_scraper': 'TODO'},
        }
    }
}


class PlaceholderCar(CarrierABC):
    def __init__(
        self,
        task: dict,
        tries_limit: int = 10,
    ):
        self.tries = 0
        self.tries_limit = tries_limit
        self.errors = []
        self.status = ResultStatus.pending.value
        self.data = {}
        self.carrier_id = task.get('carrier')
        arguments = task
        arguments.pop('carrier', None)
        self.arguments = arguments
        self.parsed_urls = []
        self.current_url = None
        self.current_page = START_PAGE_INDEX

    def run(self) -> ResultModel:
        # Handle pagination and scrape multiple pages
        self.current_url = self.current_url or self.build_url(
            URL_TEMPLATE,page=self.current_page, **self.arguments)

        response = self._get_request(self.current_url)
        self.parsed_urls.append(self.current_url)

        if response.status_code == 404 and self.current_page > START_PAGE_INDEX:
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

        # last page not reached yet
        self.current_page += 1
        self.current_url = self.build_url(URL_TEMPLATE, page=self.current_page, **self.arguments)
        self._scrape_html(response.text)
        return self._make_result()

    def _make_result(self) -> ResultModel:
        return ResultModel(
            status=self.status,
            carrier=self.carrier_id,
            arguments=self.arguments,
            urls=self.parsed_urls,
            errors=self.errors,
            data=self.data,
        )

    def _scrape_html(self, html_text: str) -> None:
        html = BeautifulSoup(html_text, 'html.parser')

        if self.current_page == START_PAGE_INDEX:
            for k, v in SINGLE_CSS_MAPPING.items():
                self.data[k] = self._scrape_fields(html, v)

        for k, v in ARRAY_CSS_MAPPING.items():
            self.data[k] = self.data.get(k, [])
            for _html in html.css.select(v['css_selector']):
                self.data[k].append(self._scrape_fields(_html, v['fields']))
