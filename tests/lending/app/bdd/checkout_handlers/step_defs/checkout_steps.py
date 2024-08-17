from datetime import date, timedelta

import pytest
from protean import current_domain, g
from pytest_bdd import given, then, when
from pytest_bdd.parsers import cfparse

from lending import CheckoutBook, HoldStatus, HoldType, Patron, PlaceHold


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


@given("a patron is logged in")
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


@when("the patron checks out the book")
def patron_checks_out_book():
    command = CheckoutBook(
        patron_id=g.current_user.id,
        book_id=g.current_book.id,
        branch_id="1",
    )
    current_domain.process(command)


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
