import datetime
from datetime import timezone


def utcNow():
    return datetime.datetime.now(timezone.utc)
