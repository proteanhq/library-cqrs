from protean import current_domain, handle
from protean.fields import Identifier

from lending import Book, Patron, checkout
from lending.domain import lending


@lending.command(part_of="Patron")
class CheckoutBook:
    patron_id = Identifier(required=True, identifier=True)
    book_id = Identifier(required=True)
    branch_id = Identifier(required=True)


@lending.command(part_of="Patron")
class ReturnBook:
    patron_id = Identifier(required=True, identifier=True)
    book_id = Identifier(required=True)


@lending.command_handler(part_of="Patron")
class CheckoutCommandHandler:
    @handle(CheckoutBook)
    def handle_checkout_book(self, command: CheckoutBook) -> None:
        patron = current_domain.repository_for(Patron).get(command.patron_id)
        book = current_domain.repository_for(Book).get(command.book_id)

        checkout(patron, book, command.branch_id)()
        current_domain.repository_for(Patron).add(patron)

    @handle(ReturnBook)
    def handle_return_book(self, command: ReturnBook) -> None:
        patron = current_domain.repository_for(Patron).get(command.patron_id)

        patron.return_book(command.book_id)
        current_domain.repository_for(Patron).add(patron)
