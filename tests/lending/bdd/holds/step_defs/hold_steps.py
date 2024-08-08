from datetime import date, timedelta

import pytest
from protean import current_domain, g
from protean.exceptions import ValidationError
from pytest_bdd import given, then, when

from lending import (
    Book,
    BookStatus,
    DailySheetService,
    HoldStatus,
    HoldType,
    Patron,
    place_hold,
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
def circulating_book(circulating_book):
    g.current_book = circulating_book


@given("a restricted book is available")
def restricted_book(restricted_book):
    g.current_book = restricted_book


@given("a regular patron is logged in")
@given("a patron is logged in")
@given("the patron is logged in")
def regular_patron(regular_patron):
    g.current_user = regular_patron


@given("a researcher patron is logged in")
def a_researcher_patron(researcher_patron):
    g.current_user = researcher_patron


@given("a book is already on hold by another patron")
def already_held_book(book):
    book.status = BookStatus.ON_HOLD.value
    current_domain.repository_for(Book).add(book)
    g.current_book = book


@given("a patron has more than two overdue checkouts at the branch")
def more_than_two_overdue_checkouts(overdue_checkouts_patron):
    g.current_user = overdue_checkouts_patron


@given("a closed-ended hold is placed")
def closed_ended_hold_placed():
    refreshed_patron = current_domain.repository_for(Patron).get(g.current_user.id)
    place_hold(refreshed_patron, g.current_book, "1", HoldType.CLOSED_ENDED)()
    current_domain.repository_for(Patron).add(refreshed_patron)


@given("the hold has reached its expiry date")
def hold_expired():
    refreshed_patron = current_domain.repository_for(Patron).get(g.current_user.id)
    refreshed_patron.holds[0].expires_on = date.today() - timedelta(days=1)
    current_domain.repository_for(Patron).add(refreshed_patron)


@given("patron has fewer than five holds")
def patron_with_fewer_than_five_holds():
    refreshed_patron = current_domain.repository_for(Patron).get(g.current_user.id)
    assert len(refreshed_patron.holds) < 5


@given("patron has exactly five holds")
def patron_with_exactly_five_holds(five_books):
    for i in range(5):
        refreshed_patron = current_domain.repository_for(Patron).get(g.current_user.id)
        place_hold(refreshed_patron, five_books[i], "1", HoldType.CLOSED_ENDED)()
        current_domain.repository_for(Patron).add(refreshed_patron)

    refreshed_patron = current_domain.repository_for(Patron).get(g.current_user.id)
    assert len(refreshed_patron.holds) == 5


@given("a patron has an active hold")
def patron_with_active_hold(patron, book):
    g.current_user = patron
    g.current_book = book

    refreshed_patron = current_domain.repository_for(Patron).get(g.current_user.id)
    place_hold(refreshed_patron, book, "1", HoldType.CLOSED_ENDED)()
    current_domain.repository_for(Patron).add(refreshed_patron)


@given("a patron has an expired hold")
def patron_with_expired_hold(patron, book):
    g.current_user = patron
    g.current_book = book

    refreshed_patron = current_domain.repository_for(Patron).get(g.current_user.id)
    place_hold(refreshed_patron, book, "1", HoldType.CLOSED_ENDED)()
    current_domain.repository_for(Patron).add(refreshed_patron)

    refreshed_patron = current_domain.repository_for(Patron).get(g.current_user.id)
    refreshed_patron.holds[0].expires_on = date.today() - timedelta(days=1)
    current_domain.repository_for(Patron).add(refreshed_patron)


@given("a patron has a hold that has been checked out")
def patron_with_checked_out_hold(patron, book):
    g.current_user = patron
    g.current_book = book

    refreshed_patron = current_domain.repository_for(Patron).get(g.current_user.id)
    place_hold(refreshed_patron, book, "1", HoldType.CLOSED_ENDED)()
    current_domain.repository_for(Patron).add(refreshed_patron)

    refreshed_patron = current_domain.repository_for(Patron).get(g.current_user.id)
    refreshed_patron.holds[0].status = HoldStatus.CHECKED_OUT.value
    current_domain.repository_for(Patron).add(refreshed_patron)


@when("the patron places a hold on the book")
@when("the patron tries to place a hold on the book")
@when("the patron tries to place a hold on a book")
@when("the patron tries to place an additional hold")
def place_hold_on_book():
    try:
        refreshed_patron = current_domain.repository_for(Patron).get(g.current_user.id)
        place_hold(refreshed_patron, g.current_book, "1", HoldType.CLOSED_ENDED)()
        current_domain.repository_for(Patron).add(refreshed_patron)
    except ValidationError as exc:
        g.current_exception = exc


@when("the patron places an open-ended hold")
@when("the patron tries to place an open-ended hold")
def place_open_ended_hold():
    try:
        refreshed_patron = current_domain.repository_for(Patron).get(g.current_user.id)
        place_hold(refreshed_patron, g.current_book, "1", HoldType.OPEN_ENDED)()
        current_domain.repository_for(Patron).add(refreshed_patron)
    except ValidationError as exc:
        g.current_exception = exc


@when("the patron places a closed-ended hold")
def closed_ended_hold():
    try:
        refreshed_patron = current_domain.repository_for(Patron).get(g.current_user.id)
        place_hold(refreshed_patron, g.current_book, "1", HoldType.CLOSED_ENDED)()
        current_domain.repository_for(Patron).add(refreshed_patron)
    except ValidationError as exc:
        g.current_exception = exc


@when("the system checks for expiring holds")
def check_expiring_holds():
    refreshed_patron = current_domain.repository_for(Patron).get(g.current_user.id)
    DailySheetService(patrons=[refreshed_patron]).run()
    current_domain.repository_for(Patron).add(refreshed_patron)


@when("the patron places more than five holds")
def place_more_than_five_holds(five_books):
    for i in range(5):
        refreshed_patron = current_domain.repository_for(Patron).get(g.current_user.id)
        place_hold(refreshed_patron, five_books[i], "1", HoldType.CLOSED_ENDED)()
        current_domain.repository_for(Patron).add(refreshed_patron)

    # Place one more hold
    refreshed_patron = current_domain.repository_for(Patron).get(g.current_user.id)
    place_hold(refreshed_patron, g.current_book, "1", HoldType.CLOSED_ENDED)()
    current_domain.repository_for(Patron).add(refreshed_patron)


@when("the patron cancels the hold")
@when("the patron tries to cancel the hold")
def cancel_hold():
    refreshed_patron = current_domain.repository_for(Patron).get(g.current_user.id)

    try:
        refreshed_patron.cancel_hold(refreshed_patron.holds[0].id)
        current_domain.repository_for(Patron).add(refreshed_patron)
    except ValidationError as exc:
        g.current_exception = exc


@then("the hold is successfully placed")
def hold_placed():
    refreshed_patron = current_domain.repository_for(Patron).get(g.current_user.id)
    assert len(refreshed_patron.holds) == 1
    assert refreshed_patron.holds[0].book_id == g.current_book.id

    if hasattr(g, "current_exception"):
        print(g.current_exception.messages)
    assert hasattr(g, "current_exception") is False


@then("the book is marked as held")
def confirm_book_marked_as_held():
    repo = current_domain.repository_for(Book)
    book = repo.get(g.current_book.id)
    assert book.status == BookStatus.ON_HOLD.value


@then("the book is not marked as held")
def confirm_book_not_marked_as_held():
    repo = current_domain.repository_for(Book)
    book = repo.get(g.current_book.id)
    assert book.status == BookStatus.AVAILABLE.value


@then("all holds are successfully placed")
def holds_placed(five_books):
    refreshed_patron = current_domain.repository_for(Patron).get(g.current_user.id)

    assert len(refreshed_patron.holds) == 6
    assert refreshed_patron.holds[0].book_id == five_books[0].id
    assert refreshed_patron.holds[5].book_id == g.current_book.id

    if hasattr(g, "current_exception"):
        print(g.current_exception.messages)
    assert hasattr(g, "current_exception") is False


@then("the hold placement is rejected")
def hold_rejected():
    assert hasattr(g, "current_exception")
    assert isinstance(g.current_exception, ValidationError)


@then("the hold status is updated to expired")
def check_hold_expired():
    refreshed_patron = current_domain.repository_for(Patron).get(g.current_user.id)
    assert refreshed_patron.holds[0].status == HoldStatus.EXPIRED.value


@then("the hold is successfully canceled")
def check_hold_canceled():
    refreshed_patron = current_domain.repository_for(Patron).get(g.current_user.id)
    assert refreshed_patron.holds[0].status == HoldStatus.CANCELLED.value


@then("the cancellation is rejected")
def check_hold_cancellation_rejected():
    assert hasattr(g, "current_exception")
    assert isinstance(g.current_exception, ValidationError)


@then("the hold does not have an expiry date")
def confirm_no_expiry_date():
    refreshed_patron = current_domain.repository_for(Patron).get(g.current_user.id)
    assert refreshed_patron.holds[0].expires_on is None
