from datetime import datetime, timedelta

from protean import invariant
from protean.fields import Identifier
from protean.exceptions import ValidationError

from lending import (
    Hold,
    HoldStatus,
    HoldType,
    HoldPlaced,
    Patron,
    PatronType,
    Book,
    BookType,
    BookStatus,
)
from lending.domain import lending


@lending.domain_service(part_of=[Patron, Book])
class place_hold:
    def __init__(
        self, patron: Patron, book: Book, branch_id: Identifier, hold_type: HoldType
    ):
        self.patron = patron
        self.book = book
        self.branch_id = branch_id
        self.hold_type = hold_type

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

    @invariant.pre
    def book_already_on_hold_cannot_be_placed_on_hold(self):
        if self.book.status == BookStatus.ON_HOLD.value:
            raise ValidationError({"book": ["Book is already on hold"]})

    @invariant.pre
    def regular_patrons_cannot_place_open_ended_holds(self):
        if (
            self.patron.patron_type == PatronType.REGULAR.value
            and self.hold_type == HoldType.OPEN_ENDED
        ):
            raise ValidationError(
                {"hold_type": ["Regular patrons cannot place open-ended holds"]}
            )

    @invariant.pre
    def regular_patron_is_limited_to_five_holds(self):
        if (
            self.patron.patron_type == PatronType.REGULAR.value
            and len(self.patron.holds) >= 5
        ):
            raise ValidationError(
                {"regular_patron_holds": ["Regular patron is limited to 5 holds"]}
            )

    @invariant.pre
    def patron_cannot_not_have_more_than_two_overdue_checkouts_in_branch(self):
        overdue_checkouts_in_branch = [
            checkout
            for checkout in self.patron.checkouts
            if checkout.due_date < datetime.now()
            and checkout.branch_id == self.branch_id
        ]
        if len(overdue_checkouts_in_branch) > 2:
            raise ValidationError(
                {
                    "overdue_checkouts_in_branch": [
                        "Patron has more than two overdue checkouts in the branch"
                    ]
                }
            )

    def __call__(self):
        hold = Hold(
            book_id=self.book.id,
            branch_id=self.branch_id,
            hold_type=self.hold_type.value,
            status=HoldStatus.ACTIVE.value,
            request_date=datetime.now(),
            expiry_date=datetime.now() + timedelta(days=7),
        )
        self.patron.add_holds(hold)

        self.patron.raise_(
            HoldPlaced(
                patron_id=self.patron.id,
                patron_type=self.patron.patron_type,
                hold_id=hold.id,
                book_id=hold.book_id,
                branch_id=hold.branch_id,
                hold_type=hold.hold_type,
                request_date=hold.request_date,
                expiry_date=hold.expiry_date
            )
        )
