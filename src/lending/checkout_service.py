from datetime import datetime, timedelta

from protean import invariant
from protean.exceptions import ValidationError
from protean.fields import Identifier

from lending.domain import lending
from lending import Patron, Book, Checkout, HoldStatus, BookType, PatronType


@lending.domain_service(part_of=[Patron, Book])
class checkout:
    def __init__(self, patron: Patron, book: Book, branch_id: Identifier):
        self.patron = patron
        self.book = book
        self.branch_id = branch_id

    @invariant.pre
    def regular_patron_cannot_place_hold_on_restricted_book(self):
        if (
            self.book.book_type == BookType.RESTRICTED.value
            and self.patron.patron_type == PatronType.REGULAR.value
        ):
            raise ValidationError(
                {
                    "restricted": [
                        "Regular patron cannot place a hold on a restricted book"
                    ]
                }
            )

    def __call__(self):
        self.patron.add_checkouts(
            Checkout(
                book_id=self.book.id,
                branch_id=self.branch_id,
                checkout_date=datetime.now(),
                due_date=datetime.now() + timedelta(days=60),
            )
        )

        # Find and update hold corresponding to book if it exists
        try:
            hold = next(h for h in self.patron.holds if h.book_id == self.book.id)
        except StopIteration:
            hold = None

        if hold:
            hold.status = HoldStatus.CHECKED_OUT.value
            self.patron.add_holds(hold)
