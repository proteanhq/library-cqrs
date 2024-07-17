from datetime import date, timedelta
from typing import Union

from protean import handle
from protean.exceptions import ObjectNotFoundError
from protean.fields import Auto, Date, DateTime, Identifier, String

from lending import Checkout, CheckoutStatus, Hold, HoldStatus
from lending.domain import lending
from lending.model.patron import (
    BookCheckedOut,
    BookOverdue,
    BookReturned,
    HoldCancelled,
    HoldExpired,
    HoldPlaced,
)


@lending.view
class DailySheet:
    id = Auto(identifier=True)
    patron_id = Identifier(required=True)
    patron_type = String(required=True)
    hold_id = Identifier()
    hold_book_id = Identifier()
    hold_branch_id = Identifier()
    hold_type = String()
    hold_status = String()
    hold_requested_at = DateTime()
    hold_expires_on = Date()
    checkout_id = Identifier()
    checkout_book_id = Identifier()
    checkout_branch_id = Identifier()
    checkout_checked_out_at = DateTime()
    checkout_status = String()
    checkout_due_on = Date()
    checkout_returned_at = DateTime()
    checkout_overdue_at = DateTime()


@lending.repository(part_of=DailySheet)
class DailySheetRepository:
    def find_hold_for_patron(self, patron_id, hold_id) -> Union[Hold, None]:
        daily_sheet_record = None
        try:
            daily_sheet_record = self._dao.find_by(
                patron_id=patron_id,
                hold_id=hold_id,
            )
        except ObjectNotFoundError:
            pass

        return daily_sheet_record

    def find_checkout_for_patron(self, patron_id, checkout_id) -> Union[Checkout, None]:
        daily_sheet_record = None
        try:
            daily_sheet_record = self._dao.find_by(
                patron_id=patron_id,
                checkout_id=checkout_id,
            )
        except ObjectNotFoundError:
            pass

        return daily_sheet_record

    def expiring_holds(self, on=date.today() - timedelta(days=1)):
        return (
            self._dao.query.filter(
                hold_status=HoldStatus.ACTIVE.value,
                hold_expires_on=on,
            )
            .all()
            .items
        )

    def expired_holds(self):
        return (
            self._dao.query.filter(
                hold_status=HoldStatus.EXPIRED.value,
            )
            .all()
            .items
        )

    def checkouts_to_be_marked_overdue(self, on=date.today() - timedelta(days=1)):
        return (
            self._dao.query.filter(
                checkout_status=CheckoutStatus.ACTIVE.value,
                checkout_due_on=on,
            )
            .all()
            .items
        )

    def overdue_checkouts(self):
        return (
            self._dao.query.filter(
                checkout_status=CheckoutStatus.OVERDUE.value,
            )
            .all()
            .items
        )


@lending.event_handler(stream_category="library::patron")
class DailySheetManager:
    @handle(HoldExpired)
    def handle_hold_expired(self, event: HoldExpired):
        repo = lending.repository_for(DailySheet)

        daily_sheet_record = repo.find_hold_for_patron(
            patron_id=event.patron_id,
            hold_id=event.hold_id,
        )

        if daily_sheet_record:
            daily_sheet_record.hold_status = HoldStatus.EXPIRED.value
        else:
            daily_sheet_record = DailySheet(
                patron_id=event.patron_id,
                patron_type=event.patron_type,
                hold_id=event.hold_id,
                hold_status=HoldStatus.EXPIRED.value,
                hold_book_id=event.book_id,
                hold_branch_id=event.branch_id,
                hold_type=event.hold_type,
                hold_requested_at=event.requested_at,
                hold_expires_on=event.expires_on,
            )

        repo.add(daily_sheet_record)

    @handle(HoldPlaced)
    def handle_hold_placed(self, event: HoldPlaced):
        repo = lending.repository_for(DailySheet)

        daily_sheet_record = repo.find_hold_for_patron(
            patron_id=event.patron_id,
            hold_id=event.hold_id,
        )

        if daily_sheet_record:
            daily_sheet_record.hold_status = HoldStatus.EXPIRED.value
        else:
            daily_sheet_record = DailySheet(
                patron_id=event.patron_id,
                patron_type=event.patron_type,
                hold_id=event.hold_id,
                hold_status=HoldStatus.ACTIVE.value,
                hold_book_id=event.book_id,
                hold_branch_id=event.branch_id,
                hold_type=event.hold_type,
                hold_requested_at=event.requested_at,
                hold_expires_on=event.expires_on,
            )

        repo.add(daily_sheet_record)

    @handle(HoldCancelled)
    def handle_hold_cancelled(self, event: HoldCancelled):
        repo = lending.repository_for(DailySheet)

        daily_sheet_record = repo.find_hold_for_patron(
            patron_id=event.patron_id,
            hold_id=event.hold_id,
        )

        if daily_sheet_record:
            daily_sheet_record.hold_status = HoldStatus.CANCELLED.value
        else:
            daily_sheet_record = DailySheet(
                patron_id=event.patron_id,
                patron_type=event.patron_type,
                hold_id=event.hold_id,
                hold_status=HoldStatus.CANCELLED.value,
                hold_book_id=event.book_id,
                hold_branch_id=event.branch_id,
                hold_type=event.hold_type,
                hold_requested_at=event.requested_at,
                hold_expires_on=event.expires_on,
            )

        repo.add(daily_sheet_record)

    @handle(BookCheckedOut)
    def handle_book_checked_out(self, event: BookCheckedOut):
        repo = lending.repository_for(DailySheet)

        daily_sheet_record = repo.find_checkout_for_patron(
            patron_id=event.patron_id,
            checkout_id=event.checkout_id,
        )

        if daily_sheet_record:
            daily_sheet_record.checkout_id = event.checkout_id
            daily_sheet_record.checkout_book_id = event.book_id
            daily_sheet_record.checkout_branch_id = event.branch_id
            daily_sheet_record.checkout_checked_out_at = event.checked_out_at
            daily_sheet_record.checkout_due_on = event.due_on
            daily_sheet_record.checkout_status = "ACTIVE"
        else:
            daily_sheet_record = DailySheet(
                patron_id=event.patron_id,
                patron_type=event.patron_type,
                checkout_id=event.checkout_id,
                checkout_book_id=event.book_id,
                checkout_branch_id=event.branch_id,
                checkout_checked_out_at=event.checked_out_at,
                checkout_due_on=event.due_on,
                checkout_status="ACTIVE",
            )

        repo.add(daily_sheet_record)

    @handle(BookReturned)
    def handle_book_returned(self, event: BookReturned):
        repo = lending.repository_for(DailySheet)

        daily_sheet_record = repo.find_checkout_for_patron(
            patron_id=event.patron_id,
            checkout_id=event.checkout_id,
        )

        if daily_sheet_record:
            daily_sheet_record.checkout_returned_at = event.returned_at
            daily_sheet_record.checkout_status = "RETURNED"
        else:
            daily_sheet_record = DailySheet(
                patron_id=event.patron_id,
                patron_type=event.patron_type,
                checkout_id=event.checkout_id,
                checkout_book_id=event.book_id,
                checkout_branch_id=event.branch_id,
                checkout_checked_out_at=event.checked_out_at,
                checkout_due_on=event.due_on,
                checkout_returned_at=event.returned_at,
                checkout_status="RETURNED",
            )

        repo.add(daily_sheet_record)

    @handle(BookOverdue)
    def handle_book_overdue(self, event: BookOverdue):
        repo = lending.repository_for(DailySheet)

        daily_sheet_record = repo.find_checkout_for_patron(
            patron_id=event.patron_id,
            checkout_id=event.checkout_id,
        )

        if daily_sheet_record:
            daily_sheet_record.checkout_overdue_at = event.checked_out_at
            daily_sheet_record.checkout_status = "OVERDUE"
        else:
            daily_sheet_record = DailySheet(
                patron_id=event.patron_id,
                patron_type=event.patron_type,
                checkout_id=event.checkout_id,
                checkout_book_id=event.book_id,
                checkout_branch_id=event.branch_id,
                checkout_checked_out_at=event.checked_out_at,
                checkout_due_on=event.due_on,
                checkout_overdue_at=event.checked_out_at,
                checkout_status="OVERDUE",
            )

        repo.add(daily_sheet_record)
