import time
from queue import Queue
from unittest.mock import MagicMock

import pytest

from app.background_jobs.http_result_aggregator import HttpResultAggregator
from app.datetime_utils import utcNow
from app.models import HttpSuccessResult


class TestHttpResultAggregator:
    def test_create_with_batch_size_zero(self):
        with pytest.raises(ValueError):
            HttpResultAggregator(MagicMock(), Queue(), 0)

    def test_start(self):
        aggregator = HttpResultAggregator(MagicMock(), Queue(), 10)
        assert aggregator.start()
        assert not aggregator.start()

    def test_stop(self):
        aggregator = HttpResultAggregator(MagicMock(), Queue(), 10)
        assert not aggregator.stop()
        aggregator.start()
        assert aggregator.stop()

    @pytest.mark.parametrize(
        "queue_size, batch_size, expected_save_calls",
        [(1, 1, 1), (10, 10, 1), (500, 100, 5), (200, 1, 200), (5, 10, 1)],
    )
    def test_given_aggregator_with_batch_size_assume_save_once(
        self, queue_size, batch_size, expected_save_calls
    ):
        metrics_repository_mock = MagicMock()
        http_worker_queue = Queue()
        aggregator = HttpResultAggregator(
            metrics_repository_mock, http_worker_queue, batch_size
        )
        aggregator.start()

        success_result = HttpSuccessResult(utcNow(), "https://google.com", 1000, 200)
        for _ in range(queue_size):
            http_worker_queue.put(success_result)

        time.sleep(0.2)

        assert metrics_repository_mock.save.call_count >= expected_save_calls
        assert http_worker_queue.empty()
