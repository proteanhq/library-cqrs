from enum import Enum

from protean.fields import HasMany, Float, String

from lending.domain import lending


@lending.aggregate
class Book:
    isbn = String(max_length=25, required=True)
    title = String(max_length=255, required=True)
    price = Float(required=True)
    book_instances = HasMany("BookInstance")


class BookInstanceStatus(Enum):
    AVAILABLE = "AVAILABLE"
    ON_HOLD = "ON_HOLD"
    CHECKED_OUT = "CHECKED_OUT"


class BookInstanceType(Enum):
    CIRCULATING = "CIRCULATING"
    RESERVED = "RESERVED"


@lending.entity(part_of=Book)
class BookInstance:
    book_instance_type = String(
        max_length=11,
        required=True,
        choices=BookInstanceType,
        default=BookInstanceType.CIRCULATING.value,
    )
    status = String(
        max_length=11,
        choices=BookInstanceStatus,
        default=BookInstanceStatus.AVAILABLE.value,
    )
