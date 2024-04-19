import time
from queue import Full as QueueFullException
from queue import Queue

from app.app_logging import getLogger
from app.background_jobs.background_job import BackgroundJob
from app.models import HttpCheckTrigger


class WebMonitorTrigger(BackgroundJob):
    def __init__(self, config: HttpCheckTrigger, triggers_queue: Queue):
        super().__init__()
        self.__config = config
        self.__queue = triggers_queue
        self.__logger = getLogger("WebMonitorTrigger")

    def _execute(self):
        while self._is_running:
            try:
                for http_check_config in self.__config.http_configs:
                    self.__queue.put_nowait(http_check_config)
                    self.__logger.debug(
                        "Put URL into triggers queue", url=http_check_config.url
                    )
                time.sleep(self.__config.interval)
            except QueueFullException:
                self.__logger.error("Triggers queue is full.")
            except BaseException:
                self.__logger.exception("Unhandled exception has occurred.")
