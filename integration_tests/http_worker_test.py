import time
from queue import Queue

import pytest

from app.background_jobs.http_result_aggregator import HttpResultAggregator
from app.background_jobs.http_worker import HttpWorker
from app.http_client import get
from app.models import HttpCheckConfig
from integration_tests.helpers import *


class TestHttpWorker:
    @pytest.fixture(autouse=True)
    def setup(self):
        cleanup_database()

    def test(self):
        NUMBER_OF_CHECKS = 20
        AGGREGATOR_BATCH_SIZE = 50
        NUMBER_OF_HTTP_WORKERS = 5
        NUMBER_OF_AGGREGATORS = 3
        SLEEP_SECONDS = 10
        QUEUE_MAX_SIZE = 10000

        triggers_queue, worker_result_queue = Queue(QUEUE_MAX_SIZE), Queue(
            QUEUE_MAX_SIZE
        )

        background_jobs = []
        for _ in range(NUMBER_OF_HTTP_WORKERS):
            background_jobs.append(HttpWorker(get, triggers_queue, worker_result_queue))

        for _ in range(NUMBER_OF_AGGREGATORS):
            background_jobs.append(
                HttpResultAggregator(
                    createHttpResultRepository(),
                    worker_result_queue,
                    AGGREGATOR_BATCH_SIZE,
                )
            )

        for job in background_jobs:
            job.start()

        for _ in range(NUMBER_OF_CHECKS):
            triggers_queue.put_nowait(HttpCheckConfig(MOCK_SERVER_HOST, 300))

        time.sleep(SLEEP_SECONDS)

        for background_job in background_jobs:
            background_job.stop()

        assert (
            select(
                f"SELECT COUNT(*) FROM metrics WHERE request_url='{MOCK_SERVER_HOST}'"
            )[0][0]
            == NUMBER_OF_CHECKS
        )
        assert triggers_queue.empty()
        assert worker_result_queue.empty()
