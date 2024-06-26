from datetime import date, timedelta

import pytest
from protean.exceptions import ValidationError
from protean.globals import current_domain, g
from pytest_bdd import given, then, when
from pytest_bdd.parsers import cfparse

from lending import (
    Book,
    DailySheet,
    DailySheetService,
    HoldType,
    checkout,
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
def persisted_circulating_book(book):
    current_domain.repository_for(Book).add(book)
    g.current_book = book


@given("a regular patron is logged in")
@given("a patron is logged in")
@given("the patron is logged in")
def regular_patron(regular_patron):
    g.current_user = regular_patron


@given("a patron has an active hold")
@given("a closed-ended hold is placed")
def patron_with_active_hold(patron, book):
    g.current_user = patron

    g.current_book = book
    current_domain.repository_for(Book).add(book)

    place_hold(g.current_user, book, "1", HoldType.CLOSED_ENDED)()


@given("the hold has reached its expiry date")
def hold_expired():
    g.current_user.holds[0].expires_on = date.today() - timedelta(days=1)


@given("a patron has checked out a book")
@given("the patron has checked out a book")
def patron_with_checkout(regular_patron, book):
    g.current_user = regular_patron

    g.current_book = book
    current_domain.repository_for(Book).add(book)

    checkout(g.current_user, g.current_book, "1")()


@given("the checkout is beyond its due date")
def the_checkout_is_beyond_its_due_date():
    g.current_user.checkouts[0].due_on = date.today() - timedelta(days=1)


@given("the system has generated a daily sheet for expiring holds")
def generated_daily_sheet_for_expiring_holds(patron, book):
    # Log in Patron
    g.current_user = patron

    # Persist Book
    g.current_book = book
    current_domain.repository_for(Book).add(book)

    # Place Hold
    place_hold(g.current_user, g.current_book, "1", HoldType.CLOSED_ENDED)()
    current_domain.publish(g.current_user._events)

    # Expire Hold
    g.current_user.holds[0].expires_on = date.today() - timedelta(days=1)

    # Update DailySheet's expiry
    daily_sheet_repo = current_domain.repository_for(DailySheet)
    record = daily_sheet_repo.find_hold_for_patron(
        g.current_user.id, g.current_user.holds[0].id
    )
    record.hold_expires_on = date.today() - timedelta(days=1)
    daily_sheet_repo.add(record)


@given("the system has generated a daily sheet for overdue checkouts")
def generated_daily_sheet_for_overdue_checkouts(patron, book):
    # Log in Patron
    g.current_user = patron

    # Persist Book
    g.current_book = book
    current_domain.repository_for(Book).add(book)

    # Checkout Book
    checkout(g.current_user, g.current_book, "1")()
    current_domain.publish(g.current_user._events)

    # Update Book's Due Date
    g.current_user.checkouts[0].due_on = date.today() - timedelta(days=1)

    # Update DailySheet's Due Date
    daily_sheet_repo = current_domain.repository_for(DailySheet)
    record = daily_sheet_repo.find_checkout_for_patron(
        g.current_user.id, g.current_user.checkouts[0].id
    )
    record.checkout_due_on = date.today() - timedelta(days=1)
    daily_sheet_repo.add(record)


@when("the patron places a hold on the book")
@when("the patron tries to place a hold on the book")
@when("the patron tries to place a hold on a book")
@when("the patron tries to place an additional hold")
def place_hold_on_book():
    try:
        place_hold(g.current_user, g.current_book, "1", HoldType.CLOSED_ENDED)()
        current_domain.publish(g.current_user._events)
    except ValidationError as exc:
        g.current_exception = exc


@when("the patron cancels the hold")
def cancel_hold():
    patron = g.current_user
    patron.cancel_hold(patron.holds[0].id)
    current_domain.publish(g.current_user._events)


@when("the system checks for expiring holds")
@when("the system processes the overdue checkouts")
@when("the system processes the expiring holds")
def run_daily_sheet_service():
    DailySheetService(patrons=[g.current_user]).run()
    current_domain.publish(g.current_user._events)


@when("the patron checks out the book")
def checkout_book():
    try:
        checkout(g.current_user, g.current_book, "1")()
        current_domain.publish(g.current_user._events)
    except ValidationError as exc:
        g.current_exception = exc


@when("the patron returns the book")
def patron_return_book():
    try:
        g.current_user.return_book(g.current_book.id)
        current_domain.publish(g.current_user._events)
    except ValidationError as exc:
        g.current_exception = exc


@when("the system generates a daily sheet for expiring holds")
def generate_daily_sheet(patron, book):
    # Log in Patron
    g.current_user = patron

    # Persist Book
    g.current_book = book
    current_domain.repository_for(Book).add(book)

    # Place Hold
    place_hold(g.current_user, g.current_book, "1", HoldType.CLOSED_ENDED)()
    current_domain.publish(g.current_user._events)

    # Expire Hold
    g.current_user.holds[0].expires_on = date.today() - timedelta(days=1)

    # Update DailySheet's expiry
    daily_sheet_repo = current_domain.repository_for(DailySheet)
    record = daily_sheet_repo.find_hold_for_patron(
        g.current_user.id, g.current_user.holds[0].id
    )
    record.hold_expires_on = date.today() - timedelta(days=1)
    daily_sheet_repo.add(record)


@when("the system generates a daily sheet for overdue checkouts")
def generate_daily_sheet_for_overdue_checkouts(patron, book):
    # Log in Patron
    g.current_user = patron

    # Persist Book
    g.current_book = book
    current_domain.repository_for(Book).add(book)

    # Checkout Book
    checkout(g.current_user, g.current_book, "1")()
    current_domain.publish(g.current_user._events)

    # Update Book's Due Date
    g.current_user.checkouts[0].due_on = date.today() - timedelta(days=1)

    # Update DailySheet's Due Date
    daily_sheet_repo = current_domain.repository_for(DailySheet)
    record = daily_sheet_repo.find_checkout_for_patron(
        g.current_user.id, g.current_user.checkouts[0].id
    )
    record.checkout_due_on = date.today() - timedelta(days=1)
    daily_sheet_repo.add(record)


@then(cfparse("the daily sheet contains the {status} hold record"))
def confirm_daily_sheet_contains_hold(status):
    repo = current_domain.repository_for(DailySheet)
    daily_sheet = repo.find_hold_for_patron(
        g.current_user.id, g.current_user.holds[0].id
    )
    assert daily_sheet is not None
    assert daily_sheet.hold_status == status


@then(cfparse("the daily sheet contains the {status} checkout record"))
def confirm_daily_sheet_contains_checkout(status):
    repo = current_domain.repository_for(DailySheet)
    daily_sheet = repo.find_checkout_for_patron(
        g.current_user.id, g.current_user.checkouts[0].id
    )
    assert daily_sheet is not None
    assert daily_sheet.checkout_status == status


@then("the daily sheet lists all expiring holds")
def confirm_daily_sheet_contains_all_expiring_holds():
    repo = current_domain.repository_for(DailySheet)
    daily_sheets = repo.expiring_holds()
    assert len(daily_sheets) == 1
    assert daily_sheets[0].hold_status == "ACTIVE"
    assert daily_sheets[0].hold_expires_on == date.today() - timedelta(days=1)


@then("the hold statuses are updated to expired")
def confirm_hold_statuses_are_updated_to_expired():
    repo = current_domain.repository_for(DailySheet)
    daily_sheets = repo.expired_holds()
    assert len(daily_sheets) == 1
    assert daily_sheets[0].hold_status == "EXPIRED"


@then("the daily sheet lists all overdue checkouts")
def confirm_daily_sheet_contains_all_overdue_checkouts():
    repo = current_domain.repository_for(DailySheet)
    daily_sheets = repo.checkouts_to_be_marked_overdue()
    assert len(daily_sheets) == 1
    assert daily_sheets[0].checkout_status == "ACTIVE"
    assert daily_sheets[0].checkout_due_on == date.today() - timedelta(days=1)


@then("the checkouts are marked overdue")
def confirm_checkouts_are_marked_overdue():
    repo = current_domain.repository_for(DailySheet)
    daily_sheets = repo.overdue_checkouts()
    assert len(daily_sheets) == 1
    assert daily_sheets[0].checkout_status == "OVERDUE"
