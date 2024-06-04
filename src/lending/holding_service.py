from datetime import datetime, timedelta

from lending import Hold, HoldStatus, HoldType, Patron, Book, BookInstance
from lending.domain import lending



@lending.domain_service(part_of=[Patron, Book])
class HoldingService:
    def __init__(self, patron: Patron, book: Book, book_instance: BookInstance):
        self.patron = patron
        self.book = book
        self.book_instance = book_instance

    def place_hold(self):
        hold = Hold(
            book_instance_id=self.book_instance.id,
            hold_type=HoldType.CLOSED_ENDED.value,
            status=HoldStatus.ACTIVE.value,
            request_date=datetime.now(),
            expiry_date=datetime.now() + timedelta(days=7),
        )
        self.patron.add_holds(hold)
