from collections import defaultdict
from typing import List, Tuple

import psycopg2

from app.data_access.query_executor import PostgreSqlQueryExecutor
from app.models import HttpFailedResult, HttpSuccessResult
from app.type_aliases import HttpResult


class HttpResultRepository:
    def __init__(self, query_executor: PostgreSqlQueryExecutor):
        self.__query_executor = query_executor
        self.METRICS_TABLE_INSERT_QUERY = "INSERT INTO metrics (request_timestamp, request_url, response_time, http_status_code, page_content) VALUES (%s, %s, %s, %s, %s);"
        self.ERRORS_TABLE_INSERT_QUERY = "INSERT INTO errors (request_timestamp, request_url, error) VALUES (%s, %s, %s);"

    def save(self, http_results: List[HttpResult]) -> None:
        # TODO: logger
        queries: defaultdict[str, List[Tuple]] = defaultdict(list)
        for result in http_results:
            query, parameters = self.__mapToSql(result)
            queries[query].append(parameters)

        for query, parameters_list in queries.items():
            self.__query_executor.insert(query, parameters_list)

    def __mapToSql(self, http_result: HttpResult) -> tuple[str, tuple]:
        match http_result:
            case HttpSuccessResult():
                return (
                    self.METRICS_TABLE_INSERT_QUERY,
                    (
                        http_result.requestTimeStamp,
                        http_result.requestUrl,
                        http_result.responseTime,
                        http_result.statusCode,
                        http_result.content,
                    ),
                )
            case HttpFailedResult():
                return (
                    self.ERRORS_TABLE_INSERT_QUERY,
                    (
                        http_result.requestTimeStamp,
                        http_result.requestUrl,
                        http_result.error,
                    ),
                )
            case _:
                raise TypeError("Trying to match unknown HttpResult")


def createRepository(
    min_conn: int,
    max_conn: int,
    db_name: str,
    user_name: str,
    db_password: str,
    db_host: str,
    db_port: int,
) -> HttpResultRepository:
    connection_pool = psycopg2.pool.SimpleConnectionPool(
        minconn=min_conn,
        maxconn=max_conn,
        dbname=db_name,
        user=user_name,
        password=db_password,
        host=db_host,
        port=db_port,
    )

    return HttpResultRepository(PostgreSqlQueryExecutor(connection_pool))
