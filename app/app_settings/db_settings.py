from app.app_settings.configuration import readConfigOptionFromEnvironment

DATABASE_NAME = "web_monitors_db"
DB_MIN_CONNECTIONS = 1
DB_MAX_CONNECTIONS = int(readConfigOptionFromEnvironment("DB_MAX_CONNECTIONS", "20"))
DB_USER_NAME = readConfigOptionFromEnvironment("DB_USER_NAME")
DB_USER_PASSWORD = readConfigOptionFromEnvironment("DB_USER_PASSWORD")
DB_HOST = readConfigOptionFromEnvironment("DB_HOST")
DB_PORT = int(readConfigOptionFromEnvironment("DB_PORT"))
