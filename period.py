# This script keeps track of the time periods by which users can filter the currency thing blockchain statistics

from enum import Enum

class Period(Enum):
    DAILY   = 1, 'in the last 24h'
    WEEKLY  = 7, 'this week'
    MONTHLY = 31, 'this month'
    ALL     = 0, 'total'

def str_to_enum(string) -> Period:
    try:
        return str2enum[string]
    except:
        return Period.DAILY


str2enum = {
    'daily'     : Period.DAILY,
    'weekly'    : Period.WEEKLY,
    'monthly'   : Period.MONTHLY,
    'all'       : Period.ALL
}

class TimePeriod:

    def __init__(self, name: str, period: Period, string) -> None:
        self.name   = name
        self.period = period
        self.string = string

