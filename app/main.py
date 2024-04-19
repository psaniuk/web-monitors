from app.app_bootstrapper import start, stop
from app.app_logging import getLogger


def main():
    logger = getLogger("main")
    try:
        start()
        logger.info("Started successfully!")
        while True:
            continue
    except BaseException as exp:
        logger.exception(exp)
        logger.info("Shutting down...")
        stop()


if __name__ == "__main__":
    main()
