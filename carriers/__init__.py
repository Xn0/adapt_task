from .models import ParserConfig
from .mock_ind import config as mock_conf
from .placeholder_car import config as placeholder_conf

CARRIER_MAPPING = {
    'MOCK_INDEMNITY': mock_conf,
    'PLACEHOLDER_CARRIER': placeholder_conf,
}


def get_carrier_conf(carrier_id: str) -> ParserConfig | None:
    if carrier_id not in CARRIER_MAPPING:
        print(f'Error: {carrier_id=} not found')
        return None

    return CARRIER_MAPPING[carrier_id]
