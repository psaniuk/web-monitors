import pytest

from app.datetime_utils import utcNow
from app.models import HttpFailedResult, HttpSuccessResult
from integration_tests.helpers import *


class TestMetricsRepository:
    @pytest.mark.parametrize("success_results_size", [1, 7])
    def test_given_success_http_result_save_assume_saved_successfully(
        self, success_results_size
    ):
        repository = createHttpResultRepository()
        http_results = [
            HttpSuccessResult(utcNow(), "https://test.io/__health", 1000, 200)
        ] * success_results_size
        repository.save(http_results)

        rows = select(f"SELECT COUNT(*) FROM metrics")
        assert rows[0][0] == success_results_size

    @pytest.mark.parametrize("failed_results_size", [1, 5])
    def test_given_failed_http_result_assume_saved_successfully(
        self, failed_results_size
    ):
        repository = createHttpResultRepository()
        failed_result = [
            HttpFailedResult(utcNow(), "https://test.io/__health", "Unknown exception")
        ] * failed_results_size
        repository.save(failed_result)
        rows = select(f"SELECT COUNT(*) FROM errors")
        assert rows[0][0] == failed_results_size

    def test_given_success_and_failed_results_assume_saved_successfully(self):
        repository = createHttpResultRepository()
        success = HttpSuccessResult(utcNow(), "https://test.io/__health", 1000, 200)
        failed = HttpFailedResult(
            utcNow(), "https://test.io/__health", "Unknown exception"
        )
        repository.save([failed, success])
        metrics_counter = select(f"SELECT COUNT(*) FROM metrics")[0][0]
        assert metrics_counter == 1
        errors_counter = select(f"SELECT COUNT(*) FROM errors")[0][0]
        assert errors_counter == 1

    @pytest.fixture(autouse=True)
    def setup(self):
        cleanup_database()
