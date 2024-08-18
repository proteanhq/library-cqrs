from datetime import date, timedelta

import pytest
from protean import current_domain, g
from protean.exceptions import ValidationError
from pytest_bdd import given, then, when

from lending import (
    Book,
    BookStatus,
    CancelHold,
    CheckoutBook,
    DailySheetService,
    HoldStatus,
    HoldType,
    Patron,
    PlaceHold,
)


@pytest.fixture(autouse=True)
def reset_globals():
    yield

    if hasattr(g, "current_user"):
        delattr(g, "current_user")
    if hasattr(g, "current_book"):
        delattr(g, "current_book")
    if hasattr(g, "current_exception"):
        delattr(g, "current_exception")


@given("a circulating book is available")
def a_circulating_book_is_available(circulating_book):
    g.current_book = circulating_book


@given("a restricted book is available")
def a_restricted_book_is_available(restricted_book):
    g.current_book = restricted_book


@given("a regular patron is logged in")
@given("a patron is logged in")
@given("the patron is logged in")
def a_regular_patron_is_logged_in(regular_patron):
    g.current_user = regular_patron


@given("a researcher patron is logged in")
def a_researcher_patron_is_logged_in(researcher_patron):
    g.current_user = researcher_patron


@given("a patron has more than two overdue checkouts at the branch")
def more_than_two_overdue_checkouts(overdue_checkouts_patron):
    g.current_user = overdue_checkouts_patron


@given("a book is already on hold by another patron")
def a_book_is_already_on_hold_by_another_patron(book):
    book.status = BookStatus.ON_HOLD.value
    current_domain.repository_for(Book).add(book)
    g.current_book = book


@given("a patron has an active hold")
@given("a closed-ended hold is placed")
def patron_with_active_hold(patron, book):
    g.current_user = patron
    g.current_book = book

    command = PlaceHold(
        patron_id=g.current_user.id,
        book_id=g.current_book.id,
        branch_id="1",
        hold_type=HoldType.CLOSED_ENDED.value,
    )
    current_domain.process(command)


@given("a patron has an expired hold")
def patron_with_expired_hold(patron, book):
    g.current_user = patron
    g.current_book = book

    command = PlaceHold(
        patron_id=g.current_user.id,
        book_id=g.current_book.id,
        branch_id="1",
        hold_type=HoldType.CLOSED_ENDED.value,
    )
    current_domain.process(command)

    refreshed_patron = current_domain.repository_for(Patron).get(g.current_user.id)
    refreshed_patron.holds[0].expires_on = date.today() - timedelta(days=1)
    current_domain.repository_for(Patron).add(refreshed_patron)


@given("the hold has reached its expiry date")
def hold_has_reached_expiry_date():
    refreshed_patron = current_domain.repository_for(Patron).get(g.current_user.id)
    refreshed_patron.holds[0].expires_on = date.today() - timedelta(days=1)
    current_domain.repository_for(Patron).add(refreshed_patron)


@given("a patron has a hold that has been checked out")
def patron_with_hold_that_has_been_checked_out(patron, book):
    g.current_user = patron
    g.current_book = book

    command = PlaceHold(
        patron_id=g.current_user.id,
        book_id=g.current_book.id,
        branch_id="1",
        hold_type=HoldType.CLOSED_ENDED.value,
    )
    current_domain.process(command)

    command = CheckoutBook(
        patron_id=g.current_user.id,
        book_id=g.current_book.id,
        branch_id="1",
    )
    current_domain.process(command)


@given("patron has fewer than five holds")
def patron_has_fewer_than_five_holds():
    refreshed_patron = current_domain.repository_for(Patron).get(g.current_user.id)
    assert len(refreshed_patron.holds) < 5


@given("patron has exactly five holds")
def patron_has_exactly_five_holds(five_books):
    for i in range(5):
        refreshed_patron = current_domain.repository_for(Patron).get(g.current_user.id)
        command = PlaceHold(
            patron_id=refreshed_patron.id,
            book_id=five_books[i].id,
            branch_id="1",
            hold_type=HoldType.CLOSED_ENDED.value,
        )
        current_domain.process(command)

    refreshed_patron = current_domain.repository_for(Patron).get(g.current_user.id)
    assert len(refreshed_patron.holds) == 5


@when("the patron places more than five holds")
def patron_places_more_than_five_holds(five_books):
    for i in range(5):
        command = PlaceHold(
            patron_id=g.current_user.id,
            book_id=five_books[i].id,
            branch_id="1",
            hold_type=HoldType.CLOSED_ENDED.value,
        )
        current_domain.process(command)

    # Place one more hold
    command = PlaceHold(
        patron_id=g.current_user.id,
        book_id=g.current_book.id,
        branch_id="1",
        hold_type=HoldType.CLOSED_ENDED.value,
    )
    current_domain.process(command)


@when("the patron places a hold on the book")
@when("the patron tries to place a hold on the book")
@when("the patron tries to place a hold on a book")
@when("the patron tries to place an additional hold")
def the_patron_places_a_hold_on_the_book():
    try:
        command = PlaceHold(
            patron_id=g.current_user.id,
            book_id=g.current_book.id,
            branch_id="1",
            hold_type=HoldType.CLOSED_ENDED.value,
        )
        current_domain.process(command)
    except ValidationError as exc:
        g.current_exception = exc


@when("the patron cancels the hold")
@when("the patron tries to cancel the hold")
def cancel_hold():
    try:
        refreshed_patron = current_domain.repository_for(Patron).get(g.current_user.id)
        command = CancelHold(
            patron_id=refreshed_patron.id,
            hold_id=refreshed_patron.holds[0].id,
        )

        current_domain.process(command)
    except ValidationError as exc:
        g.current_exception = exc


@when("the patron places an open-ended hold")
@when("the patron tries to place an open-ended hold")
def patron_places_open_ended_hold():
    try:
        command = PlaceHold(
            patron_id=g.current_user.id,
            book_id=g.current_book.id,
            branch_id="1",
            hold_type=HoldType.OPEN_ENDED.value,
        )
        current_domain.process(command)
    except ValidationError as exc:
        g.current_exception = exc


@when("the patron places a closed-ended hold")
def patron_places_closed_ended_hold():
    try:
        command = PlaceHold(
            patron_id=g.current_user.id,
            book_id=g.current_book.id,
            branch_id="1",
            hold_type=HoldType.CLOSED_ENDED.value,
        )
        current_domain.process(command)
    except ValidationError as exc:
        g.current_exception = exc


@when("the system checks for expiring holds")
def check_expiring_holds():
    refreshed_patron = current_domain.repository_for(Patron).get(g.current_user.id)
    DailySheetService(patrons=[refreshed_patron]).run()
    current_domain.repository_for(Patron).add(refreshed_patron)


@then("the hold is successfully placed")
def the_hold_is_successfully_placed():
    message = current_domain.event_store.store.read_last_message(
        f"library::patron-{g.current_user.id}"
    )
    assert message.metadata.type == "Library.HoldPlaced.v1"


@then("the book is marked as held")
def the_book_is_marked_as_held():
    book = current_domain.repository_for(Book).get(g.current_book.id)
    assert book.status == BookStatus.ON_HOLD.value


@then("the hold placement is rejected")
@then("the cancellation is rejected")
def action_is_rejected():
    assert hasattr(g, "current_exception")
    assert isinstance(g.current_exception, ValidationError)


@then("the book is not marked as held")
def the_book_is_not_marked_as_held():
    book = current_domain.repository_for(Book).get(g.current_book.id)
    assert book.status != BookStatus.ON_HOLD.value


@then("the hold is successfully canceled")
def check_hold_canceled():
    refreshed_patron = current_domain.repository_for(Patron).get(g.current_user.id)
    assert refreshed_patron.holds[0].status == HoldStatus.CANCELLED.value


@then("all holds are successfully placed")
def holds_placed(five_books):
    refreshed_patron = current_domain.repository_for(Patron).get(g.current_user.id)

    assert len(refreshed_patron.holds) == 6
    assert refreshed_patron.holds[0].book_id == five_books[0].id
    assert refreshed_patron.holds[5].book_id == g.current_book.id

    if hasattr(g, "current_exception"):
        print(g.current_exception.messages)
    assert hasattr(g, "current_exception") is False


@then("the hold does not have an expiry date")
def hold_does_not_have_expiry_date():
    refreshed_patron = current_domain.repository_for(Patron).get(g.current_user.id)
    assert refreshed_patron.holds[0].expires_on is None


@then("the hold status is updated to expired")
def hold_status_updated_to_expired():
    refreshed_patron = current_domain.repository_for(Patron).get(g.current_user.id)
    assert refreshed_patron.holds[0].status == HoldStatus.EXPIRED.value
