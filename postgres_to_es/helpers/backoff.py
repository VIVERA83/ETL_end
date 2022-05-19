import logging
from functools import wraps
from time import sleep


# Спасибо, надеюсь я тебя правильно понял, и так можно передавать уровень
def backoff(start_sleep_time=0.1, factor=2, border_sleep_time=10, logging_level=logging.ERROR):
    """
    Функция для повторного выполнения функции через некоторое время, если возникла ошибка.
    Использует наивный экспоненциальный рост времени
    повтора (factor) до граничного времени ожидания (border_sleep_time)

    Формула:
        t = start_sleep_time * 2^(n) if t < border_sleep_time
        t = border_sleep_time if t >= border_sleep_time
    :param start_sleep_time: начальное время повтора
    :param factor: во сколько раз нужно увеличить время ожидания
    :param border_sleep_time: граничное время ожидания
    :param logging_level: уровень лог оповещения
    :return: результат выполнения функции
    """

    def func_wrapper(func):
        @wraps(func)
        def inner(*args, **kwargs):
            time_sleep, n = 0, 0
            while True:
                try:
                    sleep(time_sleep)
                    func(*args, **kwargs)
                except KeyboardInterrupt:
                    logging.log(logging_level, f" {__name__.upper()}.backoff, прерван пользователем")
                    break
                except Exception as ex:
                    logging.log(logging_level, f"Ошибка {__name__}.backoff в обернутой функции:\n{func.__name__}\n{ex}")
                else:
                    n = 0
                time_sleep = (
                    start_sleep_time * factor ** n
                    if time_sleep < border_sleep_time
                    else border_sleep_time
                )
                n += 1

        return inner

    return func_wrapper


def before_execution(sleep_time=2, limit_repeat=50, logging_level=logging.ERROR):
    def func_wrapper(func):
        @wraps(func)
        def inner(*args, **kwargs):
            limit = limit_repeat
            sec = sleep_time
            while limit:
                try:
                    func(*args, **kwargs)
                    logging.log(logging_level, "  before_execution, ЗАДАЧА ВЫПОЛНЕНА")
                    break
                except KeyboardInterrupt:
                    logging.log(logging_level, "  before_execution, прерван пользователем")
                    break
                except Exception as ex:
                    logging.log(logging_level, f" before_execution, {ex}")
                logging.log(logging_level, f" before_execution, продолжаем пытаться выполнить, осталось "
                                           f"{limit} попыток")
                limit -= 1
                sleep(sec)

        return inner

    return func_wrapper
