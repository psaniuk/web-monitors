import time
from queue import Queue

import pytest

from app.background_jobs.http_result_aggregator import HttpResultAggregator
from app.background_jobs.http_worker import HttpWorker
from app.background_jobs.web_monitor import WebMonitorTrigger
from app.http_client import get
from app.models import HttpCheckConfig, HttpCheckTrigger
from integration_tests.helpers import *


class TestWebMonitor:
    @pytest.fixture(autouse=True)
    def setup(self):
        cleanup_database()

    def test(self):
        NUMBER_OF_HTTP_WORKERS = 2
        AGGREGATOR_BATCH_SIZE = 5
        NUMBER_OF_AGGREGATORS = 3
        HTTP_CHECK_INTERVAL = 5
        SLEEP_SECONDS = 8
        NUMBER_OF_CHECKS = 5

        triggers_queue, http_result_queue = Queue(), Queue()

        http_checks = [HttpCheckConfig(MOCK_SERVER_HOST, 300)] * NUMBER_OF_CHECKS
        trigger = HttpCheckTrigger(HTTP_CHECK_INTERVAL, http_checks)

        background_jobs = []
        web_monitor = WebMonitorTrigger(trigger, triggers_queue)
        background_jobs.append(web_monitor)

        for _ in range(NUMBER_OF_HTTP_WORKERS):
            background_jobs.append(HttpWorker(get, triggers_queue, http_result_queue))

        for _ in range(NUMBER_OF_AGGREGATORS):
            background_jobs.append(
                HttpResultAggregator(
                    createHttpResultRepository(),
                    http_result_queue,
                    AGGREGATOR_BATCH_SIZE,
                )
            )

        for task in background_jobs:
            task.start()

        time.sleep(SLEEP_SECONDS)

        for task in background_jobs:
            task.stop()

        multiplier = SLEEP_SECONDS // 5 + 1
        assert (
            select(
                f"SELECT COUNT(*) FROM metrics WHERE request_url='{MOCK_SERVER_HOST}'"
            )[0][0]
            == NUMBER_OF_CHECKS * multiplier
        )

        assert triggers_queue.empty()
        assert http_result_queue.empty()
