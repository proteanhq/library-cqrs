from protean import current_domain, handle
from protean.fields import Identifier, String

from lending import Book, Patron, place_hold
from lending.domain import lending


@lending.command(part_of="Patron")
class PlaceHold:
    patron_id = Identifier(required=True)
    book_id = Identifier(required=True)
    branch_id = Identifier(required=True)
    hold_type = String(required=True)


@lending.command(part_of="Patron")
class CancelHold:
    patron_id = Identifier(required=True)
    hold_id = Identifier(required=True)


@lending.command_handler(part_of="Patron")
class HoldCommandHandler:
    @handle(PlaceHold)
    def handle_place_hold(self, command: PlaceHold) -> None:
        patron = current_domain.repository_for(Patron).get(command.patron_id)
        book = current_domain.repository_for(Book).get(command.book_id)

        place_hold(patron, book, command.branch_id, command.hold_type)()
        current_domain.repository_for(Patron).add(patron)

    @handle(CancelHold)
    def handle_cancel_hold(self, command: CancelHold) -> None:
        patron = current_domain.repository_for(Patron).get(command.patron_id)
        patron.cancel_hold(command.hold_id)
        current_domain.repository_for(Patron).add(patron)
