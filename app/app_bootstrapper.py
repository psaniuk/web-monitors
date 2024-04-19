from queue import Queue
from typing import List

from app.app_logging import configureLogger, getLogger
from app.app_settings.configuration import (
    ENV,
    HTTP_RESULTS_QUEUE_MAX_SIZE,
    LOG_LEVEL,
    TRIGGERS_QUEUE_MAX_SIZE,
    loadHttpTriggerConfigs,
)
from app.app_settings.db_settings import *
from app.app_settings.http_worker_settings import *
from app.app_settings.result_aggregator_settings import *
from app.background_jobs.background_job import BackgroundJob
from app.background_jobs.http_result_aggregator import HttpResultAggregator
from app.background_jobs.http_worker import HttpWorker
from app.background_jobs.web_monitor import WebMonitorTrigger
from app.data_access.http_result_repository import createRepository
from app.http_client import get
from app.models import HttpCheckTrigger


def _setupHttpAggregators(http_result_queue: Queue) -> List[BackgroundJob]:
    repository = createRepository(
        DB_MIN_CONNECTIONS,
        DB_MAX_CONNECTIONS,
        DATABASE_NAME,
        DB_USER_NAME,
        DB_USER_PASSWORD,
        DB_HOST,
        DB_PORT,
    )
    return [
        HttpResultAggregator(
            repository, http_result_queue, RESULT_AGGREGATOR_BATCH_SIZE
        )
        for _ in range(RESULT_AGGREGATORS_NUMBER)
    ]


def _setupHttpWorkers(
    triggers_queue: Queue, http_result_queue: Queue
) -> List[BackgroundJob]:
    return [
        HttpWorker(get, triggers_queue, http_result_queue)
        for _ in range(HTTP_WORKERS_NUMBER)
    ]


def _setupWebMonitors(
    triggers: List[HttpCheckTrigger], triggers_queue: Queue
) -> List[BackgroundJob]:
    return [WebMonitorTrigger(trigger, triggers_queue) for trigger in triggers]


_app_background_jobs = []


def start():
    configureLogger(LOG_LEVEL)
    logger = getLogger("app_bootstrapper")
    logger.info(f"Starting web monitors app with {ENV} configuration...")

    triggers_queue, http_result_queue = Queue(TRIGGERS_QUEUE_MAX_SIZE), Queue(
        int(HTTP_RESULTS_QUEUE_MAX_SIZE)
    )

    logger.info("Setting up web monitors...")

    global _app_background_jobs
    counter, triggers_config = loadHttpTriggerConfigs()
    logger.debug(f"Loaded a configuration with {counter} URLs.")
    _app_background_jobs += _setupWebMonitors(triggers_config, triggers_queue)

    logger.info("Setting up http workers...")
    _app_background_jobs += _setupHttpWorkers(triggers_queue, http_result_queue)

    logger.info("Setting up http aggregators...")
    _app_background_jobs += _setupHttpAggregators(http_result_queue)

    logger.info("Starting jobs...")
    for job in _app_background_jobs:
        job.start()


def stop():
    logger = getLogger("app_bootstrapper")
    logger.info("Stopping jobs...")
    for job in _app_background_jobs:
        job.stop()
    logger.info("All background jobs has been stopped")
