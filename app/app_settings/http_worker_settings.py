from app.app_settings.configuration import readConfigOptionFromEnvironment

HTTP_WORKERS_NUMBER = int(readConfigOptionFromEnvironment("HTTP_WORKERS_NUMBER", "10"))
