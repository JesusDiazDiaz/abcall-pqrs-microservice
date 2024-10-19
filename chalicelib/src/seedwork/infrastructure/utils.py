import datetime
import os
import time
from functools import wraps
epoch = datetime.datetime.utcfromtimestamp(0)


def time_millis():
    return int(time.time() * 1000)


def unix_time_millis(dt):
    return (dt - epoch).total_seconds() * 1000.0


def handle_db_session(db_session):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            finally:
                db_session.remove()
        return wrapper
    return decorator