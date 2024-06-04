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


@lending.event(part_of="Patron")
class HoldExpired:
    """Event raised when a hold on a book placed by a patron expires."""
    patron_id = Identifier(required=True)
    hold_id = Identifier(required=True)
    branch_id = Identifier(required=True)
    book_id = Identifier(required=True)
    hold_type = String(required=True)
    request_date = DateTime(required=True)
    expiry_date = DateTime(required=True)


@lending.entity(part_of="Patron")
class Hold:
    """A reservation placed by a patron on a book.
    Holds can be open-ended or closed-ended."""

    book_id = Identifier(required=True)
    branch_id = Identifier(required=True)
    hold_type = String(max_length=12, default=HoldType.CLOSED_ENDED.value)
    status = String(max_length=10, default=HoldStatus.ACTIVE.value)
    request_date = DateTime(required=True)
    expiry_date = DateTime(required=True)


@lending.entity(part_of="Patron")
class Checkout:
    """The action of a patron borrowing a book from the library
    for a period of up to 60 days."""

    book_id = Identifier(required=True)
    branch_id = Identifier(required=True)
    checkout_date = DateTime(required=True)
    due_date = DateTime(required=True)


@lending.aggregate
class Patron:
    """A user of the public library who can place holds on books, check out books,
    and interact with their current holds and checkouts via their patron profile.
    Patrons can be either regular patrons or researcher patrons."""

    patron_type = String(max_length=10, default=PatronType.REGULAR.value)
    holds = HasMany("Hold")
    checkouts = HasMany("Checkout")

    def expire(self, hold: Hold):
        hold.status = HoldStatus.EXPIRED.value
        self.add_holds(hold)  # This updates the existing hold
        self.raise_(
            HoldExpired(
                patron_id=self.id,
                hold_id=hold.id,
                branch_id=hold.branch_id,
                book_id=hold.book_id,
                hold_type=hold.hold_type,
                request_date=hold.request_date,
                expiry_date=hold.expiry_date,
            )
        )
