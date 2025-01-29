from bs4 import BeautifulSoup

from .carrier import CarrierABC
from .models import ResultStatus, ResultModel

URL_TEMPLATE = 'https://scraping-interview.onrender.com/mock_indemnity/<customerId>'
SINGLE_CSS_MAPPING = {
    'agent': {
        'name': {'css_selector': '.agent-detail .value-name'},
        'producer_code': {'css_selector': '.agent-detail .value-producerCode'},
        'agency_name': {'css_selector': '.agent-detail .value-agencyName'},
        'agency_code': {'css_selector': '.agent-detail .value-agencyCode'},
    },
    'customer': {
        'id': {'css_selector': '.customer-detail .value-id'},
        'name': {'css_selector': '.customer-detail .value-name'},
        'email': {'css_selector': '.customer-detail .value-email'},
        'address': {'css_selector': '.customer-detail .value-address'}
    },
}
ARRAY_CSS_MAPPING = {
    'policy': {
        'css_selector': '#policy-list .list-group-item',
        'fields': {
            'id': {'css_selector': '.id'},
            'premium': {'css_selector': '.premium', 'validator': {'method': 'TODO', 'kwargs': {'precision': 2}}},
            'status': {'css_selector': '.status'},
            'effective_date': {'css_selector': '.effectiveDate', 'validator': {'method': 'TODO', 'kwargs': {'format': '%m/%d/%y'}}},
            'termination_date': {'css_selector': '.terminationDate', 'validator': {'method': 'TODO', 'kwargs': {'format': '%m/%d/%y'}}},
            'last_payment_date': {'css_selector': '.lastPaymentDate', 'validator': {'method': 'TODO', 'kwargs': {'format': '%m/%d/%y'}}},
        }
    }
}


class MockInd(CarrierABC):
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

    def run(self) -> ResultModel:
        if self.tries > self.tries_limit:
            self.status = ResultStatus.done.value
            return self._make_result()

        self.current_url = self.current_url or self.build_url(URL_TEMPLATE, **self.arguments)
        response = self._get_request(self.current_url)
        self.parsed_urls.append(self.current_url)

        if response.status_code != 200:
            if self.tries >= self.tries_limit:
                self.errors.append(f'url: error {response.status_code}')
                self.status = ResultStatus.error.value
                return self._make_result()
            else:
                self.tries += 1

        self._scrape_html(response.text)
        self.status = ResultStatus.done.value
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

        for k, v in SINGLE_CSS_MAPPING.items():
            self.data[k] = self._scrape_fields(html, v)

        for k, v in ARRAY_CSS_MAPPING.items():
            self.data[k] = []
            for _html in html.css.select(v['css_selector']):
                self.data[k].append(self._scrape_fields(_html, v['fields']))

