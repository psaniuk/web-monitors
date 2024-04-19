import re
from datetime import datetime
from typing import Any, List, Optional, Tuple


class HttpCheckConfig:
    def __init__(
        self, url: str, timeout_ms: int, regex_pattern: Optional[re.Pattern] = None
    ):
        if not url:
            raise ValueError("URL is empty")

        if timeout_ms <= 0:
            raise ValueError("HTTP request timeout must be greater zero")

        self.__url = url
        self.__timeout = timeout_ms
        self.__regex_pattern = regex_pattern

    @property
    def url(self):
        return self.__url

    @property
    def timeout(self):
        return self.__timeout

    @property
    def regex_pattern(self):
        return self.__regex_pattern


class HttpCheckTrigger:
    def __init__(self, interval_seconds: float, http_configs: List[HttpCheckConfig]):
        if interval_seconds <= 0:
            raise ValueError("Interval must be greater zero")

        if not http_configs:
            raise ValueError("HTTP configs list is empty")

        self.__interval = interval_seconds
        self.__http_configs = http_configs

    @property
    def interval(self):
        return self.__interval

    @property
    def http_configs(self):
        return self.__http_configs


class HttpSuccessResult:
    def __init__(
        self,
        request_time_stamp: datetime,
        request_url: str,
        elapsed_second: float,
        status_code: int,
        content: Optional[str] = None,
    ):
        if elapsed_second <= 0:
            raise ValueError("Elapsed seconds must be greater zero")

        self.__request_time_stamp = request_time_stamp
        self.__request_url = request_url
        self.__response_time = elapsed_second
        self.__status_code = status_code
        self.__content = content

    @property
    def requestTimeStamp(self):
        return self.__request_time_stamp

    @property
    def requestUrl(self):
        return self.__request_url

    @property
    def responseTime(self):
        return self.__response_time

    @property
    def statusCode(self):
        return self.__status_code

    @property
    def content(self):
        return self.__content


class HttpFailedResult:
    __match_args__ = ("__request_time_stamp", "__error")

    def __init__(self, request_time_stamp: datetime, request_url: str, error: str):
        if not error:
            raise ValueError("Error can't be empty")

        self.__request_time_stamp = request_time_stamp
        self.__request_url = request_url
        self.__error = error

    @property
    def requestTimeStamp(self):
        return self.__request_time_stamp

    @property
    def requestUrl(self):
        return self.__request_url

    @property
    def error(self):
        return self.__error
