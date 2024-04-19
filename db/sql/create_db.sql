-- CREATE DATABASE web_monitors_db;

CREATE TABLE metrics (
    request_timestamp TIMESTAMP NOT NULL,
    request_url TEXT NOT NULL,
    response_time FLOAT NOT NULL,
    http_status_code INT NOT NULL,
    page_content TEXT
) PARTITION BY RANGE (request_timestamp);

CREATE INDEX idx_request_timestamp ON metrics (request_timestamp);

CREATE TABLE metrics_y2024m04 PARTITION OF metrics
    FOR VALUES FROM ('2024-04-01') TO ('2024-05-01');

CREATE TABLE metrics_y2024m05 PARTITION OF metrics
    FOR VALUES FROM ('2024-05-01') TO ('2024-06-01');

CREATE TABLE metrics_y2024m06 PARTITION OF metrics
    FOR VALUES FROM ('2024-06-01') TO ('2024-07-01');

CREATE TABLE errors (
    request_timestamp TIMESTAMP NOT NULL,
    request_url TEXT NOT NULL,
    error TEXT NOT NULL
);
