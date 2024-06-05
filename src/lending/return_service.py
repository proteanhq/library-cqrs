from protean.exceptions import ValidationError


from lending.domain import lending
from lending import CheckoutStatus, Patron, Book


@lending.domain_service(part_of=[Patron, Book])
class return_book:
    def __init__(self, patron: Patron, book: Book):
        self.patron = patron
        self.book = book

    def __call__(self):
        # Find and update checkout corresponding to book if it exists
        try:
            checkout = next(
                c for c in self.patron.checkouts if c.book_id == self.book.id
            )
        except StopIteration:
            checkout = None

        if checkout:
            checkout.status = CheckoutStatus.RETURNED.value
            self.patron.add_checkouts(checkout)
        else:
            raise ValidationError({"checkout": ["Checkout does not exist"]})
