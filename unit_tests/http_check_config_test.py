import re

import pytest

from app.models import HttpCheckConfig


class TestHttpCheckConfig:
    def test_given_url_assume_get_value(self):
        url, timeout = "https://www.aiven.io", 1000
        config = HttpCheckConfig(url, timeout)
        assert config.url == url

    def test_given_timeout_assume_get_value(self):
        url, timeout = "https://www.aiven.io", 2000
        config = HttpCheckConfig(url, timeout)
        assert config.timeout == timeout

    def test_no_regex_pattern(self):
        config = HttpCheckConfig("https://www.aiven.io", 200)
        assert config.regex_pattern == None

    def test_given_regex_pattern_assume_get_value(self):
        config = HttpCheckConfig("https://www.aiven.io", 200, re.compile(r"aiven"))
        assert config.regex_pattern is not None
        assert config.regex_pattern.match("aiven")
        assert not config.regex_pattern.match("aws")

    def test_given_empty_url_raises_exception(self):
        with pytest.raises(ValueError):
            HttpCheckConfig("", 500)

    def test_given_zero_time_interval_raises_exception(self):
        with pytest.raises(ValueError):
            HttpCheckConfig("https://www.aiven.io", 0)
