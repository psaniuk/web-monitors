import pytest

from app.models import *


class TestHttpCheckTrigger:
    def test_create(self):
        trigger = HttpCheckTrigger(5, [HttpCheckConfig("https://aiven.io", 1000)])
        assert trigger.interval == 5
        assert trigger.http_configs

    def test_create_with_zero_interval(self):
        with pytest.raises(ValueError):
            HttpCheckTrigger(0, [HttpCheckConfig("https://aiven.io", 1000)])

    def test_create_with_empty_config(self):
        with pytest.raises(ValueError):
            HttpCheckTrigger(1000, [])
