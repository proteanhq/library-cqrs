from datetime import date
from enum import Enum

from protean.exceptions import ValidationError
from protean.fields import Date, DateTime, Identifier, String

from lending.domain import lending


class HoldType(Enum):
    OPEN_ENDED = "OPEN_ENDED"
    CLOSED_ENDED = "CLOSED_ENDED"


class HoldStatus(Enum):
    ACTIVE = "ACTIVE"
    EXPIRED = "EXPIRED"
    CHECKED_OUT = "CHECKED_OUT"
    CANCELLED = "CANCELLED"


@lending.event(part_of="Patron", abstract=True)
class HoldEvent:
    patron_id = Identifier(required=True)
    patron_type = String(required=True)
    hold_id = Identifier(required=True)
    branch_id = Identifier(required=True)
    book_id = Identifier(required=True)
    hold_type = String(required=True)
    requested_at = DateTime(required=True)
    expires_on = Date()


@lending.event(part_of="Patron")
class HoldExpired(HoldEvent):
    """Event raised when a hold on a book placed by a patron expires"""


@lending.event(part_of="Patron")
class HoldPlaced(HoldEvent):
    """Event raised when a book is placed on hold"""


@lending.event(part_of="Patron")
class HoldCancelled(HoldEvent):
    """Event raised when a hold placed by a patron is cancelled"""


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
                patron_type=self._owner.patron_type,
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
