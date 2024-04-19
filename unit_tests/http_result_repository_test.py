from unittest.mock import MagicMock

import pytest

from app.data_access.http_result_repository import HttpResultRepository
from app.datetime_utils import utcNow
from app.models import HttpFailedResult, HttpSuccessResult


class TestMetricsRepository:
    @pytest.mark.parametrize("http_content", [None, "test content"])
    def test_given_success_http_result_with_content_assume_generates_expected_sql_query(
        self, http_content
    ):
        sql_executor_mock = MagicMock()
        repository = HttpResultRepository(sql_executor_mock)
        http_result = HttpSuccessResult(
            utcNow(), "https://aiven.io", 1000, 2000, http_content
        )
        repository.save([http_result])

        sql_query, sql_parameters = sql_executor_mock.insert.call_args_list[0][0]
        assert sql_query == repository.METRICS_TABLE_INSERT_QUERY
        assert sql_parameters == [
            (
                http_result.requestTimeStamp,
                http_result.requestUrl,
                http_result.responseTime,
                http_result.statusCode,
                http_result.content,
            )
        ]

    def test_give_multiple_success_results_assume_generates_expected_sql_query(self):
        sql_executor_mock = MagicMock()
        repository = HttpResultRepository(sql_executor_mock)

        http_results = [
            HttpSuccessResult(utcNow(), "https://aiven.io", 1000, 2000)
        ] * 10
        repository.save(http_results)

        sql_query, sql_parameters = sql_executor_mock.insert.call_args_list[0][0]
        assert sql_query == repository.METRICS_TABLE_INSERT_QUERY
        assert len(sql_parameters) == len(http_results)

    def test_given_failed_http_result_with_content_assume_generates_expected_sql_query(
        self,
    ):
        sql_executor_mock = MagicMock()
        repository = HttpResultRepository(sql_executor_mock)
        http_result = HttpFailedResult(utcNow(), "https://aiven.io", "error")
        repository.save([http_result])

        sql_query, sql_parameters = sql_executor_mock.insert.call_args_list[0][0]

        assert sql_query == repository.ERRORS_TABLE_INSERT_QUERY
        assert sql_parameters == [
            (http_result.requestTimeStamp, http_result.requestUrl, http_result.error)
        ]
