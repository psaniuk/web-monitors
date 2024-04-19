from datetime import datetime
from typing import Callable, Union

from app.models import HttpCheckConfig, HttpFailedResult, HttpSuccessResult

HttpResult = Union[HttpSuccessResult, HttpFailedResult]
UtcDateTimeProvider = Callable[[], datetime]
HttpClient = Callable[
    [HttpCheckConfig, UtcDateTimeProvider], Union[HttpSuccessResult, Exception]
]
