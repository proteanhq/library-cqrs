from datetime import date, datetime, timedelta
from enum import Enum

from protean.fields import Date, DateTime, Identifier, String

from lending.domain import lending
from lending.utils import utc_now


class CheckoutStatus(Enum):
    ACTIVE = "ACTIVE"
    RETURNED = "RETURNED"
    OVERDUE = "OVERDUE"


@lending.event(part_of="Patron", abstract=True)
class CheckoutEvent:
    checkout_id = Identifier(required=True)
    patron_id = Identifier(required=True)
    patron_type = String(required=True)
    book_id = Identifier(required=True)
    branch_id = Identifier(required=True)
    checked_out_at = DateTime(required=True)
    due_on = Date(required=True)


@lending.event(part_of="Patron")
class BookCheckedOut(CheckoutEvent):
    """Event raised when a patron checks out a book"""


@lending.event(part_of="Patron")
class BookReturned(CheckoutEvent):
    """Event raised when a patron returns a book"""

    returned_at = DateTime(required=True)


@lending.event(part_of="Patron")
class BookOverdue(CheckoutEvent):
    """Event raised when a book is marked overdue"""


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
