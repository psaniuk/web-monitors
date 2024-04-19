from queue import Empty as QueueEmptyException
from queue import Full as QueueFullException
from queue import Queue

from app.app_logging import getLogger
from app.background_jobs.background_job import BackgroundJob
from app.datetime_utils import utcNow
from app.type_aliases import HttpClient


class HttpWorker(BackgroundJob):
    def __init__(
        self, request: HttpClient, triggers_queue: Queue, worker_result_queue: Queue
    ):
        super().__init__()
        self.__request = request
        self.__input_queue = triggers_queue
        self.__output_queue = worker_result_queue
        self.__logger = getLogger("HttpWorker")

    def _execute(self):
        while self._is_running:
            if self.__input_queue.empty():
                continue

            try:
                item = self.__input_queue.get_nowait()
                self.__logger.debug("Processing trigger queue", url=item.url)
                result = self.__request(item, utcNow)
                self.__logger.debug(
                    "Put HTTP result in worker result queue", url=result.requestUrl
                )
                self.__output_queue.put_nowait(result)
                self.__input_queue.task_done()
            except QueueEmptyException:
                self.__logger.info("Triggers queue is empty.")
            except QueueFullException:
                self.__logger.error("Worker result queue is full.")
            except BaseException:
                self.__logger.exception("Unhandled exception has occurred.")
