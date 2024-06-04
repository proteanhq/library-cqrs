from enum import Enum

from protean.fields import String

from lending.domain import lending


class BookStatus(Enum):
    AVAILABLE = "AVAILABLE"
    ON_HOLD = "ON_HOLD"
    CHECKED_OUT = "CHECKED_OUT"


class BookType(Enum):
    CIRCULATING = "CIRCULATING"
    RESTRICTED = "RESTRICTED"


@lending.aggregate
class Book:
    isbn = String(max_length=25, required=True)
    book_type = String(
        max_length=11,
        required=True,
        choices=BookType,
        default=BookType.CIRCULATING.value,
    )
    status = String(
        max_length=11,
        choices=BookStatus,
        default=BookStatus.AVAILABLE.value,
    )
