from enum import Enum


class ProductState(Enum):
    NEW = 1
    BASKET = 2
    BUY = 3
    UNAVAILABLE = 4
    ERROR = 5
    OLD = 6
    RESERVED = 7
    UNIDENTIFIED = 8
    EXPENSIVE = 9


class DeliveryState(Enum):
    RESERVED = 0
    BAD = 1
    GOOD = 2
