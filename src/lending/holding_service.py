from datetime import datetime, timedelta

from protean import invariant
from protean.fields import Identifier
from protean.exceptions import ValidationError

from lending import Hold, HoldStatus, HoldType, Patron, PatronType, Book, BookType, BookStatus
from lending.domain import lending


@lending.domain_service(part_of=[Patron, Book])
class HoldingService:
    def __init__(self, patron: Patron, book: Book, branch_id: Identifier):
        self.patron = patron
        self.book = book
        self.branch_id = branch_id

    @invariant.pre
    def regular_patron_cannot_place_hold_on_restricted_book(self):
        if (
            self.book.book_type == BookType.RESTRICTED.value and
            self.patron.patron_type == PatronType.REGULAR.value
        ):
            raise ValidationError({"restricted": ["Regular patron cannot place a hold on a restricted book"]})

    @invariant.pre
    def book_already_on_hold_cannot_be_placed_on_hold(self):
        if self.book.status == BookStatus.ON_HOLD.value:
            raise ValidationError({"book": ["Book is already on hold"]})

    @invariant.post
    def patron_does_not_have_more_than_two_overdue_checkouts_in_branch(self):
        overdue_checkouts_in_branch = [
            checkout
            for checkout in self.patron.checkouts
            if checkout.due_date < datetime.now() and
            checkout.branch_id == self.branch_id
        ]
        if len(overdue_checkouts_in_branch) > 2:
            raise ValidationError({
                "overdue_checkouts_in_branch": [
                    "Patron has more than two overdue checkouts in the branch"
                ]
            })

    def place_hold(self):
        hold = Hold(
            book_id=self.book.id,
            branch_id=self.branch_id,
            hold_type=HoldType.CLOSED_ENDED.value,
            status=HoldStatus.ACTIVE.value,
            request_date=datetime.now(),
            expiry_date=datetime.now() + timedelta(days=7),
        )
        self.patron.add_holds(hold)
