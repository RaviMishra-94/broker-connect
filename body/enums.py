from enum import Enum


class Exchange(Enum):
    NSE = "NSE"
    BSE = "BSE"
    MCX = "MCX"

class TransactionType(Enum):
    BUY = "BUY"
    SELL = "SELL"

class Segment(Enum):
    EQUITY = "EQUITY"
    FUTURE = "FUTURE"
    OPTION = "OPTION"
    CURRENCY = "CURRENCY"
    COMMODITY = "COMMODITY"