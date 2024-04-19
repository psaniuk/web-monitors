import threading
from abc import ABC, abstractmethod


class BackgroundJob(ABC):
    def __init__(self):
        self.__stop_event = None
        self.__background_thread = None

    def start(self):
        if self.__background_thread:
            return False

        self.__stop_event = threading.Event()
        self.__background_thread = threading.Thread(target=self._execute, daemon=True)
        self.__background_thread.start()

        return True

    def stop(self):
        if not self.__background_thread:
            return False

        self.__stop_event.set()
        self.__background_thread.join()
        self.__background_thread = None

        return True

    @property
    def _is_running(self):
        return self.__stop_event and not self.__stop_event.is_set()

    @abstractmethod
    def _execute(self):
        pass
