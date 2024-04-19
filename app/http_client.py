import re
import traceback
from typing import Optional

import requests
from circuitbreaker import circuit

from app.models import HttpCheckConfig, HttpFailedResult, HttpSuccessResult
from app.type_aliases import HttpResult, UtcDateTimeProvider


@circuit
def get(
    http_config: HttpCheckConfig, datetime_provider: UtcDateTimeProvider
) -> HttpResult:
    try:
        request_timestamp = datetime_provider()

        with requests.Session() as session:
            response = session.get(
                http_config.url,
                timeout=(http_config.timeout / 1000, http_config.timeout / 1000),
            )

        contentTypeHeader = "Content-Type"
        response_content = (
            response.text
            if contentTypeHeader in response.headers
            and response.headers[contentTypeHeader] in ["text/html", "application/json"]
            else None
        )

        result_content = applyRegex(response_content, http_config.regex_pattern)

        return HttpSuccessResult(
            request_timestamp,
            http_config.url,
            response.elapsed.total_seconds(),
            response.status_code,
            result_content,
        )

    except BaseException:
        return HttpFailedResult(
            request_timestamp, http_config.url, traceback.format_exc()
        )


def applyRegex(
    http_content: Optional[str], regex: Optional[re.Pattern]
) -> Optional[str]:
    if not http_content or not regex:
        return None
    matching = re.search(regex, http_content)
    return matching.group(0) if matching else None
