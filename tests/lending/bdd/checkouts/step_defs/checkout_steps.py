import pytest

from datetime import timedelta

from pytest_bdd import given, when, then

from protean.exceptions import ValidationError

from lending import (
    place_hold,
    HoldType,
    checkout,
    BookType,
    return_book,
    CheckoutStatus,
)


@pytest.fixture(autouse=True)
def reset_globals():
    yield

    from protean.globals import g

    if hasattr(g, "current_user"):
        delattr(g, "current_user")
    if hasattr(g, "current_book"):
        delattr(g, "current_book")
    if hasattr(g, "current_exception"):
        delattr(g, "current_exception")


@given("a circulating book is available")
def circulating_book(book):
    from protean.globals import g

    g.current_book = book


@given("a restricted book is available")
def restricted_book(book):
    from protean.globals import g

    book.book_type = BookType.RESTRICTED.value
    g.current_book = book


@given("a patron is logged in")
def regular_patron(regular_patron):
    from protean.globals import g

    g.current_user = regular_patron


@given("the patron has a hold on the book")
def patron_with_active_hold(patron, book):
    from protean.globals import g

    place_hold(g.current_user, book, "1", HoldType.CLOSED_ENDED)()


@given("a patron has checked out a book")
def patron_with_checkout(regular_patron, book):
    from protean.globals import g

    g.current_user = regular_patron
    g.current_book = book

    checkout(g.current_user, g.current_book, "1")()


@given("the book is overdue")
def mark_checkout_overdue():
    from protean.globals import g

    patron = g.current_user
    patron.checkouts[0].due_date = patron.checkouts[0].due_date - timedelta(days=1)
    patron.checkouts[0].status = CheckoutStatus.OVERDUE.value


@when("the patron checks out the book")
@when("the patron tries to check out the book")
def checkout_book():
    from protean.globals import g

    try:
        checkout(g.current_user, g.current_book, "1")()
    except ValidationError as exc:
        g.current_exception = exc


@when("the patron returns the book")
def patron_return_book():
    from protean.globals import g

    try:
        return_book(g.current_user, g.current_book)()
    except ValidationError as exc:
        g.current_exception = exc


@then("the checkout is successfully completed")
def confirm_checkout_book():
    from protean.globals import g

    assert len(g.current_user.checkouts) == 1
    assert g.current_user.checkouts[0].book_id == g.current_book.id


@then("the checkout is rejected")
def confirm_checkout_rejected():
    from protean.globals import g

    assert hasattr(g, "current_exception")
    assert isinstance(g.current_exception, ValidationError)


@then("the overdue status is cleared")
def confirm_returned_status():
    from protean.globals import g

    assert g.current_user.checkouts[0].status == "RETURNED"


@then("the return is successfully processed")
def confirm_successful_return():
    from protean.globals import g

    assert hasattr(g, "current_exception") is False
