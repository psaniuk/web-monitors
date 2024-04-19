from app.datetime_utils import utcNow
from app.models import HttpFailedResult


class TestHttpFailedResult:
    def test_create(self):
        time_stamp = utcNow()
        failed_result = HttpFailedResult(time_stamp, "https://google.com", "error")
        assert (
            failed_result.requestTimeStamp == time_stamp
            and failed_result.requestUrl == "https://google.com"
            and failed_result.error == "error"
        )
