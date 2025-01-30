import requests
import time
import json

from dataclasses import asdict

from carriers import get_carrier_conf
from .models import ResultModel, ResultStatus
from .extractor import Extractor


class Worker:
    def __init__(
        self,
        delay_ms: int = 0,
    ):
        self.delay_ms = delay_ms
        self.tasks = []
        self.scraped_data = []

    def get_json_scraped_data(self):
        data = [asdict(d) for d in self.scraped_data]
        return json.dumps(data, indent=4)

    def add_tasks(self, tasks: list[dict]) -> None:
        for task in tasks:
            carrier_conf = get_carrier_conf(task.get('carrier'))
            if not carrier_conf:
                self.scraped_data.append(
                    ResultModel(
                        status=ResultStatus.error.value,
                        carrier=task.pop('carrier', None),
                        arguments=task,
                        errors=['Unknown carrier'],
                    )
                )
            else:
                self.tasks.append(Extractor(task, carrier_conf))

    def run_tasks(self) -> None:
        if not self.tasks:
            print('Task queue is empty')

        while self.tasks:
            task = self.tasks.pop()
            try:
                result = task.run()
                if result.status == ResultStatus.pending.value:
                    # Re-queue task if not completed
                    self.tasks.append(task)
                else:
                    self.scraped_data.append(result)
            except requests.HTTPError as e:
                # Handle rate limiting by increasing delay
                if e == '429':
                    self.delay_ms += 500

            time.sleep(self.delay_ms / 1000)

        print('All tasks processed')
