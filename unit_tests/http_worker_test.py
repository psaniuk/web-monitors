import time
from queue import Queue

from app.background_jobs.http_worker import HttpWorker
from app.datetime_utils import utcNow
from app.models import HttpCheckConfig, HttpSuccessResult
from app.type_aliases import HttpClient


class TestHttpWorker:
    def test_assume_cant_start_multiple_times(self):
        httpWorker = HttpWorker(self.__createHttpClient(), Queue(), Queue())
        assert httpWorker.start()
        assert not httpWorker.start()

    def test_assume_cant_stop_not_started(self):
        httpWorker = HttpWorker(self.__createHttpClient(), Queue(), Queue())
        assert not httpWorker.stop()
        httpWorker.start()
        assert httpWorker.stop()

    def test_put_item_to_triggers_queue_without_start_assume_wont_consume(self):
        triggers_queue = Queue()
        triggers_queue.put_nowait(HttpCheckConfig("https://www.aiven.io", 1000))
        httpWorker = HttpWorker(self.__createHttpClient(), triggers_queue, Queue())
        assert triggers_queue.qsize() == 1
        httpWorker.start()
        assert triggers_queue.qsize() == 0

    def test_given_started_worker_put_item_to_triggers_queue_assume_processed(self):
        triggers_queue, worker_result_queue = Queue(), Queue()
        httpWorker = HttpWorker(
            self.__createHttpClient(), triggers_queue, worker_result_queue
        )

        httpWorker.start()
        http_check = HttpCheckConfig("https://www.aiven.io", 1000)
        triggers_queue.put_nowait(http_check)

        time.sleep(0.2)

        assert triggers_queue.qsize() == 0
        assert worker_result_queue.qsize() == 1

    def test_given_started_worker_put_several_items_in_triggers_queue_assume_all_processed(
        self,
    ):
        triggers_queue, worker_result_queue = Queue(), Queue()
        httpWorker = HttpWorker(
            self.__createHttpClient(), triggers_queue, worker_result_queue
        )
        httpWorker.start()
        num_of_checks = 10
        for check in [HttpCheckConfig("https://www.aiven.io", 1000)] * num_of_checks:
            triggers_queue.put_nowait(check)

        time.sleep(0.5)

        assert triggers_queue.qsize() == 0
        assert worker_result_queue.qsize() == num_of_checks

    def test_stop_worker_assume_triggers_queue_is_not_processed(self):
        triggers_queue, worker_result_queue = Queue(), Queue()
        httpWorker = HttpWorker(
            self.__createHttpClient(), triggers_queue, worker_result_queue
        )
        httpWorker.start()

        http_check = HttpCheckConfig("https://www.aiven.io", 1000)
        triggers_queue.put_nowait(http_check)
        httpWorker.stop()
        triggers_queue.put_nowait(http_check)

        assert triggers_queue.qsize() >= 1

    def __createHttpClient(self) -> HttpClient:
        return lambda http_config, dateTimeProvider: HttpSuccessResult(
            utcNow(), "https://aiven.io", 100, 200
        )
