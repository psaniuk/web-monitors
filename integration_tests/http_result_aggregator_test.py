import time
from queue import Queue

import pytest

from app.background_jobs.http_result_aggregator import HttpResultAggregator
from app.datetime_utils import utcNow
from app.models import HttpSuccessResult
from integration_tests.helpers import *


class TestHttpResultAggregator:
    def test_given_5000_items_and_batch_size_1000_assume_processed_successfully(self):
        QUEUE_SIZE, BATCH_SIZE = 5000, 1000

        http_worker_queue = Queue(QUEUE_SIZE)
        result_aggregator = HttpResultAggregator(
            createHttpResultRepository(), http_worker_queue, BATCH_SIZE
        )
        assert result_aggregator.start()
        http_success_result = HttpSuccessResult(
            utcNow(), "https://test.com/__health", 100, 200, "some content"
        )

        for _ in range(QUEUE_SIZE):
            http_worker_queue.put_nowait(http_success_result)

        time.sleep(5)
        result_aggregator.stop()

        assert (
            select(
                "SELECT COUNT(*) from metrics WHERE request_url = 'https://test.com/__health'"
            )[0][0]
            == QUEUE_SIZE
        )

    @pytest.fixture(autouse=True)
    def setup(self):
        cleanup_database()
