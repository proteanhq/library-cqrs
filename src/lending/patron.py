from enum import Enum

from protean.fields import DateTime, HasMany, Identifier, String

from lending.domain import lending


class PatronType(Enum):
    REGULAR = "REGULAR"
    RESEARCHER = "RESEARCHER"


class HoldType(Enum):
    OPEN_ENDED = "OPEN_ENDED"
    CLOSED_ENDED = "CLOSED_ENDED"


class HoldStatus(Enum):
    ACTIVE = "ACTIVE"
    EXPIRED = "EXPIRED"
    CANCELLED = "CANCELLED"


@lending.aggregate
class Patron:
    """This is the Patron Aggregate."""

    patron_type = String(max_length=10, default=PatronType.REGULAR.value)
    holds = HasMany("Hold")
    checkouts = HasMany("Checkout")


@lending.entity(part_of=Patron)
class Hold:
    """This is the Hold Entity."""

    book_instance_id = Identifier(required=True)
    hold_type = String(max_length=12, default=HoldType.CLOSED_ENDED.value)
    status = String(max_length=10, default=HoldStatus.ACTIVE.value)
    request_date = DateTime(required=True)
    expiry_date = DateTime(required=True)


@lending.entity(part_of=Patron)
class Checkout:
    """This is the Checkout Entity."""

    book_instance_id = Identifier(required=True)
    checkout_date = DateTime(required=True)
    due_date = DateTime(required=True)
