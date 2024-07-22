from enum import Enum

from protean.exceptions import ObjectNotFoundError, ValidationError
from protean.fields import HasMany, Identifier, String

from lending.domain import lending


class PatronType(Enum):
    REGULAR = "REGULAR"
    RESEARCHER = "RESEARCHER"


@lending.aggregate(fact_events=True)
class Patron:
    """A user of the public library who can place holds on books, check out books,
    and interact with their current holds and checkouts via their patron profile.
    Patrons can be either regular patrons or researcher patrons."""

    patron_type = String(max_length=10, choices=PatronType, default="REGULAR")
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
