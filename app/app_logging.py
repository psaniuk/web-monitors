"""
Source https://betterstack.com/community/guides/logging/best-python-logging-libraries/
"""

import logging

import structlog


def configureLogger(log_level: str):
    structlog.configure(
        wrapper_class=structlog.make_filtering_bound_logger(
            logging.getLevelName(log_level)
        )
    )


def getLogger(name: str):
    return structlog.get_logger(source=name)
