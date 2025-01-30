from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, UTC


class ResultStatus(Enum):
    done = 'done'
    pending = 'pending'
    error = 'error'


@dataclass
class ResultModel:
    status: ResultStatus
    carrier: str | None
    arguments: dict
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC).isoformat())
    data: dict | None = None
    urls: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
