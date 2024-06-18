from protean import invariant
from protean.exceptions import ObjectNotFoundError, ValidationError
from protean.fields import Identifier

from lending.book import Book, BookType
from lending.domain import lending
from lending.patron import BookCheckedOut, Checkout, Patron, PatronType


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
        checkout = Checkout(
            book_id=self.book.id,
            branch_id=self.branch_id,
        )
        self.patron.add_checkouts(checkout)

        # Find and update hold corresponding to book if it exists
        hold = None
        try:
            hold = self.patron.get_one_from_holds(book_id=self.book.id)
        except ObjectNotFoundError:
            hold = None

        if hold:
            hold.checkout()

        # Raise Event
        checkout.raise_(
            BookCheckedOut(
                patron_id=self.patron.id,
                patron_type=self.patron.patron_type,
                book_id=self.book.id,
                branch_id=self.branch_id,
                checked_out_at=checkout.checked_out_at,
                due_on=checkout.due_on,
            )
        )
