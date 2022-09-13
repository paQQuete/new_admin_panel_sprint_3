import time
from functools import wraps

from psycopg2 import OperationalError

def backoff(
    exception=OperationalError,
    message="Database connection error",
    start_sleep_time=0.1,
    factor=2,
    border_sleep_time=10,
):
    """
    Функция для повторного выполнения функции через некоторое время, если возникла ошибка.
    :param start_sleep_time: начальное время повтора
    :param factor: основание степени для просчета нового времени повтора
    :param border_sleep_time: максимальное время повтора
    :return:
    """

    def wrapper(func):
        @wraps(func)
        def inner(*args, **kwargs):
            cur_sleep_time = start_sleep_time
            try_count = 1
            while True:
                try:
                    return func(*args, **kwargs)
                except exception as e:
                    logger.error(
                        message + f"{e}. Next try in {cur_sleep_time} seconds"
                    )
                    time.sleep(cur_sleep_time)
                    if cur_sleep_time < border_sleep_time:
                        cur_sleep_time *= factor**try_count
                    else:
                        cur_sleep_time = border_sleep_time
                    try_count += 1

        return inner

    return wrapper
