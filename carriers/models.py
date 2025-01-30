from dataclasses import dataclass, field

from scraper.selectors import BaseElementSelector
from scraper.extractors import BaseValueExtractor
from scraper.validators import BaseValidator
from scraper.converters import BaseConverter


@dataclass
class FieldConfig:
    name: str
    extractor: BaseValueExtractor
    selector: BaseElementSelector | None = None
    validators: list[BaseValidator] = field(default_factory=list)
    converter: BaseConverter | None = None


@dataclass
class DataConfig:
    name: str
    fields: list[FieldConfig]
    array: bool = False
    container_selector: BaseElementSelector | None = None


@dataclass
class ParserConfig:
    url_template: str
    multipage: bool
    data: list[DataConfig]
    start_page: int | None = None
