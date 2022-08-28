import time
from datetime import datetime as dt
from math import floor

import pandas as pd


# returns seconds since epoch
def sinceEpoch(date):
    return pd.DatetimeIndex([date]).astype(int)[0] / 10**9


def from_date_to_year_fraction(date):
    date = pd.Timestamp(date)
    s = sinceEpoch
    year = date.year
    startOfThisYear = dt(year=year, month=1, day=1)
    startOfNextYear = dt(year=year + 1, month=1, day=1)
    yearElapsed = s(date) - s(startOfThisYear)
    yearDuration = s(startOfNextYear) - s(startOfThisYear)
    fraction = yearElapsed / yearDuration
    return date.year + fraction


def from_year_fraction_to_date(year_fraction):
    year = floor(year_fraction)
    fraction = year_fraction - year
    startOfThisYear = dt(year=year, month=1, day=1)
    startOfNextYear = dt(year=year + 1, month=1, day=1)
    s = sinceEpoch
    yearDuration = s(startOfNextYear) - s(startOfThisYear)
    yearElapsed = fraction * yearDuration
    date_since_epoch_in_ns = (yearElapsed + s(startOfThisYear)) * 10**9
    return pd.Timestamp(date_since_epoch_in_ns, unit="ns")
