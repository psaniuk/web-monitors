import re

from app.datetime_utils import utcNow
from app.http_client import get
from app.models import HttpCheckConfig, HttpFailedResult, HttpSuccessResult


class TestHttpClient:
    def test_given_http_200_response_assume_http_success_result_returned(self):
        http_check = HttpCheckConfig("http://localhost:1080", 300)
        http_result = get(http_check, utcNow)
        assert isinstance(http_result, HttpSuccessResult)
        assert http_result.statusCode == 200

    def test_given_check_with_unreachable_url_assume_failed_result_returned(self):
        http_check = HttpCheckConfig("http://localhost:1090", 300)
        http_result = get(http_check, utcNow)
        assert isinstance(http_result, HttpFailedResult)
        assert http_result.error

    def test_given_http_404_response_assume_http_success_result_returned(self):
        http_check = HttpCheckConfig("http://localhost:1080/not_found", 300)
        http_result = get(http_check, utcNow)
        assert isinstance(http_result, HttpSuccessResult)
        assert http_result.statusCode == 404

    def test_given_check_with_timeout_50_ms_assume_http_failed_result(self):
        http_check = HttpCheckConfig("http://localhost:1080", 50)
        http_result = get(http_check, utcNow)
        assert isinstance(http_result, HttpFailedResult)

    def test_given_check_with_regex_assume_success_result_with_content(self):
        http_check = HttpCheckConfig(
            "http://localhost:1080/regex_test", 50, re.compile("Not Found")
        )
        http_result = get(http_check, utcNow)
        assert http_result.content == "Not Found"
