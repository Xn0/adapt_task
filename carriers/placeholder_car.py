from bs4 import BeautifulSoup

from scraper.selectors import CSSSingleSelector, CSSMultiSelector, CustomSelector
from scraper.extractors import HTMLValueExtractor, RegexExtractor

from .models import FieldConfig, ParserConfig, DataConfig


def hidden_tr_selector(html: BeautifulSoup) -> BeautifulSoup | None:
    _id = html.get('data-bs-target')
    parent_el = html.parent
    return parent_el.select_one(_id)


config = ParserConfig(
    url_template='https://scraping-interview.onrender.com/placeholder_carrier/<customerId>/policies/<page>',
    multipage=True,
    start_page=1,
    data=[
        DataConfig(
            name='agent',
            container_selector=CSSSingleSelector('.agency-details'),
            fields=[
                FieldConfig(
                    name='name',
                    selector=CSSSingleSelector('.nice-formatted-kv label[for="name"] + span'),
                    extractor=HTMLValueExtractor(),
                ),
                FieldConfig(
                    name='producer_code',
                    selector=CSSSingleSelector('.nice-formatted-kv label[for="producerCode"] + span'),
                    extractor=HTMLValueExtractor(),
                ),
                FieldConfig(
                    name='agency_name',
                    selector=CSSSingleSelector('.nice-formatted-kv label[for="agencyName"] + span'),
                    extractor=HTMLValueExtractor(),
                ),
                FieldConfig(
                    name='agency_code',
                    selector=CSSSingleSelector('.nice-formatted-kv label[for="agencyCode"] + span'),
                    extractor=HTMLValueExtractor(),
                ),
            ]
        ),
        DataConfig(
            name='customer',
            container_selector=CSSSingleSelector('.customer-details'),
            fields=[
                FieldConfig(
                    name='id',
                    extractor=RegexExtractor(r'(?<=Id:<\/label><span>)([^<]+)(?=<\/span>)'),
                ),
                FieldConfig(
                    name='name',
                    selector=CSSSingleSelector('label[for="name"] + span'),
                    extractor=HTMLValueExtractor(),
                ),
                FieldConfig(
                    name='ssn',
                    extractor=RegexExtractor(r'(?<=SSN:<\/label><span>)\d{9}(?=<\/span>)'),
                ),
                FieldConfig(
                    name='email',
                    extractor=RegexExtractor(r'(?<=Email:<\/label>)(.+)(?=<div>)'),
                ),
                FieldConfig(
                    name='address',
                    extractor=RegexExtractor(r'(?<=Address: )([^<]+)(?=<\/div>)'),
                ),
            ]
        ),
        DataConfig(
            name='policy',
            container_selector=CSSMultiSelector('.policy-info-row'),
            array=True,
            fields=[
                FieldConfig(
                    name='id',
                    selector=CSSSingleSelector('td:nth-child(1)'),
                    extractor=HTMLValueExtractor(),
                ),
                FieldConfig(
                    name='premium',
                    selector=CSSSingleSelector('td:nth-child(2)'),
                    extractor=HTMLValueExtractor(),
                ),
                FieldConfig(
                    name='status',
                    selector=CSSSingleSelector('td:nth-child(3)'),
                    extractor=HTMLValueExtractor(),
                ),
                FieldConfig(
                    name='effective_date',
                    selector=CSSSingleSelector('td:nth-child(4)'),
                    extractor=HTMLValueExtractor(),
                ),
                FieldConfig(
                    name='termination_date',
                    selector=CSSSingleSelector('td:nth-child(5)'),
                    extractor=HTMLValueExtractor(),
                ),
                FieldConfig(
                    name='last_payment_date',
                    selector=CustomSelector(hidden_tr_selector),
                    extractor=RegexExtractor(r'(?<=Last Payment Date: )\d{1,2}/\d{1,2}/\d{4}'),
                ),
                FieldConfig(
                    name='commission_rate',
                    selector=CustomSelector(hidden_tr_selector),
                    extractor=RegexExtractor(r'(?<=Commission Rate: )\d{1,2}%'),
                ),
                FieldConfig(
                    name='number_of_insureds',
                    selector=CustomSelector(hidden_tr_selector),
                    extractor=RegexExtractor(r'(?<=Number of Insureds: )\d+(?=<\/div>)'),
                ),
            ]
        ),
    ]
)
