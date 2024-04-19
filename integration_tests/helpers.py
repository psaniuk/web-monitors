import psycopg2

from app.data_access.http_result_repository import HttpResultRepository
from app.data_access.query_executor import PostgreSqlQueryExecutor

MOCK_SERVER_HOST = "http://0.0.0.0:1080/"

connection_pool = psycopg2.pool.SimpleConnectionPool(
    minconn=1,
    maxconn=20,
    dbname="web_monitors_db",
    user="user",
    password="pwd",
    host="0.0.0.0",
)


def select(sql_query):
    connection = connection_pool.getconn()
    try:
        with connection.cursor() as cursor:
            cursor.execute(sql_query)
            return cursor.fetchall()
    finally:
        connection.close()
        connection_pool.putconn(connection)


def delete(sql_query):
    connection = connection_pool.getconn()
    try:
        with connection.cursor() as cursor:
            cursor.execute(sql_query)
        connection.commit()
    finally:
        connection.close()
        connection_pool.putconn(connection)


def createHttpResultRepository():
    return HttpResultRepository(PostgreSqlQueryExecutor(connection_pool))


def cleanup_database():
    delete("DELETE FROM metrics")
    delete("DELETE FROM errors")
