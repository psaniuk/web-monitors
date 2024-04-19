from app.app_settings.configuration import readConfigOptionFromEnvironment

RESULT_AGGREGATORS_NUMBER = int(
    readConfigOptionFromEnvironment("RESULT_AGGREGATORS_NUMBER", "1")
)
RESULT_AGGREGATOR_BATCH_SIZE = int(
    readConfigOptionFromEnvironment("RESULT_AGGREGATOR_BATCH_SIZE", "1")
)
