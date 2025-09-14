#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import pytz
import datetime as datetime_module
from datetime import datetime, timedelta

HOUR_IN_MS = 3600000
ONE_DAY_IN_MS = 86400000
FIVE_DAYS_IN_MS = 432000000


def datetime_(year=1970, month=1, day=1, hour=0, min=0, seg=0, ms=0):
    return datetime(year, month, day, hour, min, seg, ms)


def add_time(value=None, unit="ms", base=datetime_().replace(tzinfo=pytz.utc), **kwargs):
    if len(kwargs) == 0:
        kwargs[unit] = value

    if "m" in kwargs:
        kwargs["weeks"] = 4 * int(kwargs.pop("m"))

    rename_map = {
        "ms": "milliseconds",
        "s": "seconds",
        "S": "seconds",
        "min": "minutes",
        "M": "minutes",
        "h": "hours",
        "H": "hours",
        "d": "days",
    }

    kwargs = {rename_map.get(k, k): int(v) for k, v in kwargs.items()}

    try:
        return base + timedelta(**kwargs)
    except:
        raise ValueError("Invalid time unit")


def epoch_time(date, utc=True, format=None):
    if isinstance(date, datetime_module.date) and not isinstance(
        date, datetime_module.datetime
    ):
        date = datetime.combine(date, datetime_module.time(0))

    formated_date = date if format is None else datetime.strptime(date, format)
    if not utc:
        formated_date += timedelta(hours=3)
    formated_date = formated_date.replace(tzinfo=pytz.utc)

    dt = formated_date - datetime_().replace(tzinfo=pytz.utc)

    return int(dt.total_seconds() * 1000)
