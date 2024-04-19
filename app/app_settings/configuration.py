import json
import os
import re
from collections import defaultdict
from typing import Any, List, Optional, Tuple

from dotenv import load_dotenv

from app.app_logging import getLogger
from app.models import HttpCheckConfig, HttpCheckTrigger


def readConfigOptionFromEnvironment(
    env_var_name: str, default_value: Optional[str] = None
) -> str:
    if not env_var_name:
        raise ValueError("Env var name is required.")

    logger = getLogger("readConfigOptionFromEnvironment")
    env_var_value = os.getenv(env_var_name)
    if not env_var_value:
        if not default_value:
            raise ValueError(
                f"{env_var_name} value is not configured in env vars. Please, configure and launch the app again."
            )

        logger.warning(
            f"{env_var_name} is not set in env vars. Using default {str(default_value)}."
        )
    return env_var_value if env_var_value else str(default_value)


ENV = readConfigOptionFromEnvironment("ENV", "qa")

load_dotenv(f".env.{ENV}")

LOG_LEVEL = readConfigOptionFromEnvironment("LOG_LEVEL", "INFO")
HTTP_CHECK_DEFAULT_TIMEOUT = int(
    readConfigOptionFromEnvironment("HTTP_CHECK_DEFAULT_TIMEOUT", "300")
)
TRIGGERS_QUEUE_MAX_SIZE = int(
    readConfigOptionFromEnvironment("TRIGGERS_QUEUE_MAX_SIZE", "10000")
)
HTTP_RESULTS_QUEUE_MAX_SIZE = int(
    readConfigOptionFromEnvironment("HTTP_RESULTS_QUEUE_MAX_SIZE", "10000")
)


class ConfigurationError(Exception):
    pass


def create_http_check_config(json_obj: Any) -> Tuple[int, HttpCheckConfig]:
    if "interval" not in json_obj:
        raise ConfigurationError(
            "Interval is not defined in HTTP URLs config, please validate the format."
        )

    if "url" not in json_obj:
        raise ConfigurationError(
            "URL is not defined in HTTP URLs config, please validate the format."
        )

    try:
        regex = re.compile(json_obj["regex"]) if "regex" in json_obj else None
        timeout = (
            int(json_obj["timeout"])
            if "timeout" in json_obj
            else HTTP_CHECK_DEFAULT_TIMEOUT
        )
        return (
            int(json_obj["interval"]),
            HttpCheckConfig(json_obj["url"], timeout, regex),
        )
    except re.error:
        raise ConfigurationError(
            "Regex in HTTP URLs config is not valid. Please, check the format"
        )
    except ValueError:
        raise ConfigurationError(
            "Interval or timeout value in HTTP URLs config is not valid. Please, make sure it's number > 0."
        )


def loadHttpTriggerConfigs() -> Tuple[int, List[HttpCheckTrigger]]:
    try:
        with open(f"urls.config.{ENV}.json") as urls_config_file:
            items = json.load(urls_config_file)
            
        if not items:
            raise ConfigurationError(
                "HTTP URLs are not configured. Please, define URLs to monitor in urls.config.(env_name).json file"
            )

        http_configs = map(create_http_check_config, items)
        total_count, grouped_by_interval = 0, defaultdict(list)
        for interval, http_check_config in http_configs:
            grouped_by_interval[interval].append(http_check_config)
            total_count += 1

        triggers = list(
            map(
                lambda item: HttpCheckTrigger(item[0], item[1]),
                grouped_by_interval.items(),
            )
        )

        return (total_count, triggers)
    except FileNotFoundError:
        raise ConfigurationError(
            "HTTP URLs config file is not found. Please make sure it's placed in the root directory."
        )
