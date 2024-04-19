from app.app_logging import configureLogger


def pytest_configure(config):
    configureLogger("INFO")
