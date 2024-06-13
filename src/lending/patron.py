from datetime import datetime, timezone, timedelta
from enum import Enum

from protean.exceptions import ObjectNotFoundError, ValidationError
from protean.fields import DateTime, HasMany, Identifier, String

from lending.domain import lending


def utc_now():
    return datetime.now(timezone.utc)


class PatronType(Enum):
    REGULAR = "REGULAR"
    RESEARCHER = "RESEARCHER"


class HoldType(Enum):
    OPEN_ENDED = "OPEN_ENDED"
    CLOSED_ENDED = "CLOSED_ENDED"


class HoldStatus(Enum):
    ACTIVE = "ACTIVE"
    EXPIRED = "EXPIRED"
    CHECKED_OUT = "CHECKED_OUT"
    CANCELLED = "CANCELLED"


@lending.event(part_of="Patron")
class HoldExpired:
    """Event raised when a hold on a book placed by a patron expires"""

    patron_id = Identifier(required=True)
    hold_id = Identifier(required=True)
    branch_id = Identifier(required=True)
    book_id = Identifier(required=True)
    hold_type = String(required=True)
    request_date = DateTime(required=True)
    expiry_date = DateTime(required=True)


@lending.event(part_of="Patron")
class HoldPlaced:
    """Event raised when a book is placed on hold"""

    patron_id = Identifier(required=True)
    patron_type = String(required=True)
    hold_id = Identifier(required=True)
    book_id = Identifier(required=True)
    branch_id = Identifier(required=True)
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
    status = String(max_length=11, default=HoldStatus.ACTIVE.value)
    request_date = DateTime(required=True)
    expiry_date = DateTime(required=True)

    def expire(self):
        self.status = HoldStatus.EXPIRED.value

    def cancel(self):
        if self.status == HoldStatus.EXPIRED.value or self.expiry_date < datetime.now():
            raise ValidationError({"expired_hold": ["Cannot cancel expired holds"]})

        if self.status == HoldStatus.CHECKED_OUT.value:
            raise ValidationError({"checked_out": ["Cannot cancel a checked out hold"]})

        self.status = HoldStatus.CANCELLED.value


class CheckoutStatus(Enum):
    ACTIVE = "ACTIVE"
    RETURNED = "RETURNED"
    OVERDUE = "OVERDUE"


@lending.entity(part_of="Patron")
class Checkout:
    """The action of a patron borrowing a book from the library
    for a period of up to 60 days."""

    book_id = Identifier(required=True)
    branch_id = Identifier(required=True)
    checkout_date = DateTime(required=True, default=utc_now)
    status = String(max_length=11, default=CheckoutStatus.ACTIVE.value)
    due_date = DateTime(required=True, default=lambda: utc_now() + timedelta(days=7))
    return_date = DateTime()

    def return_(self):
        self.status = CheckoutStatus.RETURNED.value
        self.return_date = datetime.now()

    def overdue(self):
        self.status = CheckoutStatus.OVERDUE.value


@lending.aggregate
class Patron:
    """A user of the public library who can place holds on books, check out books,
    and interact with their current holds and checkouts via their patron profile.
    Patrons can be either regular patrons or researcher patrons."""

    patron_type = String(max_length=10, default=PatronType.REGULAR.value)
    holds = HasMany("Hold")
    checkouts = HasMany("Checkout")

    def expire_hold(self, hold_id: Identifier):
        try:
            hold = self.get_one_from_holds(id=hold_id)
        except ObjectNotFoundError:
            raise ValidationError({"hold": ["Hold does not exist"]})

        hold.expire()

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

    def cancel_hold(self, hold_id: Identifier):
        try:
            hold = self.get_one_from_holds(id=hold_id)
        except ObjectNotFoundError:
            raise ValidationError({"hold": ["Hold does not exist"]})

        hold.cancel()

    def return_book(self, book_id: Identifier):
        try:
            checkout = self.get_one_from_checkouts(book_id=book_id)
        except ObjectNotFoundError:
            raise ValidationError({"checkout": ["Checkout does not exist"]})

        checkout.return_()
