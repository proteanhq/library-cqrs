from datetime import datetime, timedelta

from protean import invariant
from protean.exceptions import ValidationError

from lending import Hold, HoldStatus, HoldType, Patron, PatronType, Book, BookInstance, BookInstanceType
from lending.domain import lending



@lending.domain_service(part_of=[Patron, Book])
class HoldingService:
    def __init__(self, patron: Patron, book_instance: BookInstance):
        self.patron = patron
        self.book_instance = book_instance

    @invariant.pre
    def regular_patron_cannot_place_hold_on_restricted_book(self):
        if (
            self.book_instance.book_instance_type == BookInstanceType.RESTRICTED.value and
            self.patron.patron_type == PatronType.REGULAR.value
        ):
            raise ValidationError({"restricted": ["Regular patron cannot place a hold on a restricted book"]})

    def place_hold(self):
        hold = Hold(
            book_instance_id=self.book_instance.id,
            hold_type=HoldType.CLOSED_ENDED.value,
            status=HoldStatus.ACTIVE.value,
            request_date=datetime.now(),
            expiry_date=datetime.now() + timedelta(days=7),
        )
        self.patron.add_holds(hold)
