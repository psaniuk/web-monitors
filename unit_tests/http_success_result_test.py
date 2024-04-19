import pytest

from app.datetime_utils import utcNow
from app.models import HttpSuccessResult


class TestHttpSuccessResult:
    def test_create(self):
        timestamp = utcNow()
        httpSuccess = HttpSuccessResult(
            timestamp, "https://google.com", 1000, 200, "some_content"
        )
        assert httpSuccess.requestTimeStamp == timestamp
        assert httpSuccess.requestUrl == "https://google.com"
        assert httpSuccess.responseTime == 1000
        assert httpSuccess.statusCode == 200
        assert httpSuccess.content == "some_content"

    def test_create_zero_elapsed_second(self):
        with pytest.raises(ValueError):
            HttpSuccessResult(utcNow(), "https://google.com", 0, 200, "some_content")
