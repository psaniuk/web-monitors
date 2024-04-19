from queue import Empty as QueueEmptyException
from queue import Queue

from app.app_logging import getLogger
from app.background_jobs.background_job import BackgroundJob
from app.data_access.http_result_repository import HttpResultRepository


class HttpResultAggregator(BackgroundJob):
    def __init__(
        self,
        repository: HttpResultRepository,
        http_worker_queue: Queue,
        batch_size: int,
    ) -> None:
        if batch_size <= 0:
            raise ValueError("Batch size must be greater than zero.")

        super().__init__()
        self.__repository = repository
        self.__batch_size = batch_size
        self.__http_worker_queue = http_worker_queue
        self.__logger = getLogger("HttpResultAggregator")

    def _execute(self):
        buffer = []
        while self._is_running:
            try:
                if self.__http_worker_queue.empty():
                    if buffer:
                        self.__repository.save(buffer)
                        self.__logger.debug(
                            f"HTTP worker queue is empty. Saving {len(buffer)} items into database"
                        )
                        buffer = []
                    continue

                if len(buffer) >= self.__batch_size:
                    self.__repository.save(buffer)
                    self.__logger.debug(
                        f"Saving a full batch with {len(buffer)} items into database"
                    )
                    buffer = []

                worker_result = self.__http_worker_queue.get_nowait()
                self.__logger.debug(
                    "Buffering HTTP result", url=worker_result.requestUrl
                )
                buffer.append(worker_result)
                self.__http_worker_queue.task_done()
            except QueueEmptyException:
                self.__logger.warning("HTTP worker queue is empty.")
            except BaseException:
                self.__logger.exception("Unhandled exception has occurred.")

        # TODO: move to cleanup
        if buffer:
            self.__repository.save(buffer)
