from typing import Type

from .mock_ind import MockInd
from .placeholder_car import PlaceholderCar
from .carrier import CarrierABC

CARRIER_MAPPING = {
    'MOCK_INDEMNITY': MockInd,
    'PLACEHOLDER_CARRIER': PlaceholderCar,
}


def get_carrier(carrier_id: str) -> Type[CarrierABC] | None:
    if carrier_id not in CARRIER_MAPPING:
        print(f'Error: {carrier_id=} not found')
        return

    return CARRIER_MAPPING[carrier_id]
