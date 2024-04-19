from typing import List, Tuple

from psycopg2.pool import SimpleConnectionPool


class PostgreSqlQueryExecutor:
    def __init__(self, connection_pool: SimpleConnectionPool) -> None:
        self.__connection_pool = connection_pool

    def insert(self, query: str, parameters: List[Tuple]):
        if not query or not parameters:
            return

        connection = self.__connection_pool.getconn()

        try:
            with connection.cursor() as cursor:
                cursor.executemany(query, parameters)
                connection.commit()
        finally:
            connection.close()
            self.__connection_pool.putconn(connection)
