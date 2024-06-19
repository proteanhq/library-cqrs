from datetime import date, datetime, timedelta, timezone
from enum import Enum

from protean.exceptions import ObjectNotFoundError, ValidationError
from protean.fields import Date, DateTime, HasMany, Identifier, String

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
    requested_at = DateTime(required=True)
    expires_on = Date()


@lending.event(part_of="Patron")
class HoldPlaced:
    """Event raised when a book is placed on hold"""

    patron_id = Identifier(required=True)
    patron_type = String(required=True)
    hold_id = Identifier(required=True)
    book_id = Identifier(required=True)
    branch_id = Identifier(required=True)
    hold_type = String(required=True)
    requested_at = DateTime(required=True)
    expires_on = Date()


@lending.event(part_of="Patron")
class HoldCancelled:
    """Event raised when a hold placed by a patron is cancelled"""

    patron_id = Identifier(required=True)
    patron_type = String(required=True)
    hold_id = Identifier(required=True)
    branch_id = Identifier(required=True)
    book_id = Identifier(required=True)
    hold_type = String(required=True)
    requested_at = DateTime(required=True)
    expires_on = Date()


@lending.entity(part_of="Patron")
class Hold:
    """A reservation placed by a patron on a book.
    Holds can be open-ended or closed-ended."""

    book_id = Identifier(required=True)
    branch_id = Identifier(required=True)
    hold_type = String(max_length=12, default=HoldType.CLOSED_ENDED.value)
    status = String(max_length=11, default=HoldStatus.ACTIVE.value)
    requested_at = DateTime(required=True)
    expires_on = Date()

    def checkout(self):
        self.status = HoldStatus.CHECKED_OUT.value

    def expire(self):
        self.status = HoldStatus.EXPIRED.value

        self.raise_(
            HoldExpired(
                patron_id=self._owner.id,
                hold_id=self.id,
                branch_id=self.branch_id,
                book_id=self.book_id,
                hold_type=self.hold_type,
                requested_at=self.requested_at,
                expires_on=self.expires_on,
            )
        )

    def cancel(self):
        if self.status == HoldStatus.EXPIRED.value or self.expires_on < date.today():
            raise ValidationError({"expired_hold": ["Cannot cancel expired holds"]})

        if self.status == HoldStatus.CHECKED_OUT.value:
            raise ValidationError({"checked_out": ["Cannot cancel a checked out hold"]})

        self.status = HoldStatus.CANCELLED.value

        self.raise_(
            HoldCancelled(
                patron_id=self._owner.id,
                patron_type=self._owner.patron_type,
                hold_id=self.id,
                book_id=self.book_id,
                branch_id=self.branch_id,
                hold_type=self.hold_type,
                requested_at=self.requested_at,
                expires_on=self.expires_on,
            )
        )


class CheckoutStatus(Enum):
    ACTIVE = "ACTIVE"
    RETURNED = "RETURNED"
    OVERDUE = "OVERDUE"


@lending.event(part_of="Patron")
class BookCheckedOut:
    """Event raised when a patron checks out a book"""

    checkout_id = Identifier(required=True)
    patron_id = Identifier(required=True)
    patron_type = String(required=True)
    book_id = Identifier(required=True)
    branch_id = Identifier(required=True)
    checked_out_at = DateTime(required=True)
    due_on = Date(required=True)


@lending.event(part_of="Patron")
class BookReturned:
    """Event raised when a patron returns a book"""

    checkout_id = Identifier(required=True)
    patron_id = Identifier(required=True)
    patron_type = String(required=True)
    book_id = Identifier(required=True)
    branch_id = Identifier(required=True)
    checked_out_at = DateTime(required=True)
    due_on = Date(required=True)
    returned_at = DateTime(required=True)


@lending.event(part_of="Patron")
class BookOverdue:
    """Event raised when a book is marked overdue"""

    checkout_id = Identifier(required=True)
    patron_id = Identifier(required=True)
    patron_type = String(required=True)
    book_id = Identifier(required=True)
    branch_id = Identifier(required=True)
    checked_out_at = DateTime(required=True)
    due_on = Date(required=True)


@lending.entity(part_of="Patron")
class Checkout:
    """The action of a patron borrowing a book from the library
    for a period of up to 60 days."""

    book_id = Identifier(required=True)
    branch_id = Identifier(required=True)
    checked_out_at = DateTime(required=True, default=utc_now)
    status = String(max_length=11, default=CheckoutStatus.ACTIVE.value)
    due_on = Date(
        required=True,
        default=lambda: date.today()
        + timedelta(days=lending.config["custom"]["CHECKOUT_PERIOD"]),
    )
    returned_at = DateTime()

    def return_(self):
        self.status = CheckoutStatus.RETURNED.value
        self.returned_at = datetime.now()

        self.raise_(
            BookReturned(
                checkout_id=self.id,
                patron_id=self._owner.id,
                patron_type=self._owner.patron_type,
                book_id=self.book_id,
                branch_id=self.branch_id,
                checked_out_at=self.checked_out_at,
                due_on=self.due_on,
                returned_at=self.returned_at,
            )
        )

    def overdue(self):
        self.status = CheckoutStatus.OVERDUE.value

        self.raise_(
            BookOverdue(
                checkout_id=self.id,
                patron_id=self._owner.id,
                patron_type=self._owner.patron_type,
                book_id=self.book_id,
                branch_id=self.branch_id,
                checked_out_at=self.checked_out_at,
                due_on=self.due_on,
            )
        )


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
