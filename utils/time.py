
import datetime
import time


def convert(time):
    time_dict = {
        's': 1,
        'm': 60,
        'h': 3600,
        'd': 3600 * 24,
        'w': 3600 * 24 * 7,
        'y': 3600 * 24 * 365
    }

    unit = time[-1]

    if unit not in time_dict:
        return -1
    try:
        value = int(time[:-1])
    except Exception:
        return -2
    if value <= 0:
        return -3

    if unit == 's':
        real_unit = 'second(s)'
    if unit == 'm':
        real_unit = 'minute(s)'
    if unit == 'h':
        real_unit = 'hour(s)'
    if unit == 'd':
        real_unit = 'day(s)'
    if unit == 'w':
        real_unit = 'week(s)'
    if unit == 'y':
        real_unit = 'year(s)'

    return [value * time_dict[unit], value, real_unit]


def datetime_to_seconds(thing: datetime.datetime):
    current_time = datetime.datetime.fromtimestamp(time.time())
    return round(round(time.time()) + (current_time - thing.replace(tzinfo=None)).total_seconds())


def convert_int_to_weekday(number: int) -> str:
    weekdays = {
        0: 'Monday',
        1: 'Tuesday',
        2: 'Wednesday',
        3: 'Thursday',
        4: 'Friday',
        5: 'Saturday',
        6: 'Sunday'
    }
    return weekdays[number]
