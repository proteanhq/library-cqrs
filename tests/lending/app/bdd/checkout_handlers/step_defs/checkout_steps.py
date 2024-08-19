from datetime import date, timedelta

import pytest
from protean import UnitOfWork, current_domain, g
from pytest_bdd import given, then, when
from pytest_bdd.parsers import cfparse

from lending import (
    Book,
    Checkout,
    CheckoutBook,
    CheckoutStatus,
    DailySheetService,
    HoldStatus,
    HoldType,
    Patron,
    PlaceHold,
    ReturnBook,
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
def circulating_book_available(book):
    g.current_book = book


@given("a restricted book is available")
def restricted_book(restricted_book):
    g.current_book = restricted_book


@given("a patron is logged in")
@given("a regular patron is logged in")
def patron_logged_in(regular_patron):
    g.current_user = regular_patron


@given("the patron has a hold on the book")
def patron_has_hold_on_book():
    command = PlaceHold(
        patron_id=g.current_user.id,
        book_id=g.current_book.id,
        branch_id="1",
        hold_type=HoldType.CLOSED_ENDED.value,
    )
    current_domain.process(command)


@given("a patron has checked out a book")
def patron_with_checkout(regular_patron, book):
    g.current_user = regular_patron
    g.current_book = book

    command = CheckoutBook(
        patron_id=g.current_user.id,
        book_id=g.current_book.id,
        branch_id="1",
    )
    try:
        current_domain.process(command)
    except Exception as e:
        g.current_exception = e


@given("the system has overdue checkouts")
def system_has_overdue_checkouts():
    patron1 = Patron()
    current_domain.repository_for(Patron).add(patron1)
    patron2 = Patron()
    current_domain.repository_for(Patron).add(patron2)

    book1 = Book(isbn="1234567890123")
    current_domain.repository_for(Book).add(book1)
    book2 = Book(isbn="1234567890124")
    current_domain.repository_for(Book).add(book2)
    book3 = Book(isbn="1234567890125")
    current_domain.repository_for(Book).add(book3)

    patron1 = current_domain.repository_for(Patron).get(patron1.id)
    patron2 = current_domain.repository_for(Patron).get(patron2.id)

    patron1.add_checkouts(
        [
            Checkout(
                book_id=book1.id,
                branch_id="1",
            ),
            Checkout(
                book_id=book2.id,
                branch_id="1",
            ),
        ]
    )
    # Manually expire a checkout
    patron1.checkouts[0].due_on = date.today() - timedelta(days=1)

    patron2.add_checkouts(
        Checkout(
            book_id=book3.id,
            branch_id="1",
        )
    )
    # Manually exipre a checkout
    patron2.checkouts[0].due_on = date.today() - timedelta(days=1)

    current_domain.repository_for(Patron).add(patron1)
    current_domain.repository_for(Patron).add(patron2)

    g.current_patrons = [patron1, patron2]
    g.patron1_checkout_overdue_id = patron1.checkouts[0].id
    g.patron2_checkout_overdue_id = patron2.checkouts[0].id


@given("the book is overdue")
def mark_checkout_overdue():
    patron = current_domain.repository_for(Patron).get(g.current_user.id)

    patron.checkouts[0].due_on = date.today() - timedelta(days=1)
    patron.checkouts[0].status = CheckoutStatus.OVERDUE.value

    current_domain.repository_for(Patron).add(patron)


@when("the patron checks out the book")
@when("the patron tries to check out the book")
def patron_checks_out_book():
    command = CheckoutBook(
        patron_id=g.current_user.id,
        book_id=g.current_book.id,
        branch_id="1",
    )
    try:
        current_domain.process(command)
    except Exception as e:
        g.current_exception = e


@when("the system processes the overdue checkouts")
def process_overdue_checkouts():
    with UnitOfWork():
        patron1 = current_domain.repository_for(Patron).get(g.current_patrons[0].id)
        patron2 = current_domain.repository_for(Patron).get(g.current_patrons[1].id)
        DailySheetService(patrons=[patron1, patron2]).run()

        current_domain.repository_for(Patron).add(patron1)
        current_domain.repository_for(Patron).add(patron2)


@when("the patron returns the book")
def patron_returns_book():
    command = ReturnBook(
        patron_id=g.current_user.id,
        book_id=g.current_book.id,
    )
    try:
        current_domain.process(command)
    except Exception as e:
        g.current_exception = e


@then("the checkout is successfully completed")
def checkout_completed():
    message = current_domain.event_store.store.read_last_message(
        f"library::patron-{g.current_user.id}"
    )
    assert message.metadata.type == "Library.BookCheckedOut.v1"


@then(cfparse("the checkout has a validity of {validity_days_config}"))
def checkout_validity(validity_days_config):
    patron = current_domain.repository_for(Patron).get(g.current_user.id)
    checkout = patron.checkouts[0]
    assert checkout.due_on == date.today() + timedelta(
        days=current_domain.config["custom"][validity_days_config]
    )


@then("the hold is marked as checked out")
def hold_marked_checked_out():
    patron = current_domain.repository_for(Patron).get(g.current_user.id)
    hold = patron.holds[0]
    assert hold.status == HoldStatus.CHECKED_OUT.value


@then("the checkout is rejected")
def checkout_rejected():
    assert isinstance(g.current_exception, Exception)
    assert (
        str(g.current_exception)
        == "{'restricted': ['Regular patron cannot place a hold on a restricted book']}"
    )


@then("the checkouts are marked overdue")
def confirm_overdue_marking():
    patron1 = current_domain.repository_for(Patron).get(g.current_patrons[0].id)
    patron2 = current_domain.repository_for(Patron).get(g.current_patrons[1].id)

    patron1_checkout = next(
        (
            checkout
            for checkout in patron1.checkouts
            if checkout.id == g.patron1_checkout_overdue_id
        ),
        None,
    )
    patron2_checkout = next(
        (
            checkout
            for checkout in patron2.checkouts
            if checkout.id == g.patron2_checkout_overdue_id
        ),
        None,
    )
    assert patron1_checkout.status == "OVERDUE"
    assert patron2_checkout.status == "OVERDUE"

    if hasattr(g, "current_exception"):
        print(g.current_exception.messages)
    assert hasattr(g, "current_exception") is False


@then("the book is successfully returned")
def book_successfully_returned():
    book = current_domain.repository_for(Book).get(g.current_book.id)
    assert book.status == "AVAILABLE"

    assert hasattr(g, "current_exception") is False


@then("the overdue status is cleared")
def overdue_status_cleared():
    patron = current_domain.repository_for(Patron).get(g.current_user.id)
    checkout = patron.checkouts[0]
    assert checkout.status != "OVERDUE"
