import pytest

from datetime import datetime, timedelta, timezone

from pytest_bdd import given, when, then

from protean.exceptions import ValidationError

from lending import Book, Patron, Checkout

from lending import (
    place_hold,
    HoldType,
    checkout,
    BookType,
    CheckoutStatus,
    DailySheetService,
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


@given("the system has overdue checkouts")
def system_has_overdue_checkouts():
    from protean.globals import g

    patron1 = Patron()
    patron2 = Patron()

    book1 = Book(isbn="1234567890123")
    book2 = Book(isbn="1234567890124")
    book3 = Book(isbn="1234567890125")

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
    patron1.checkouts[0].due_date = datetime.now(timezone.utc) - timedelta(days=1)

    patron2.add_checkouts(
        Checkout(
            book_id=book3.id,
            branch_id="1",
        )
    )
    # Manually exipre a checkout
    patron2.checkouts[0].due_date = datetime.now(timezone.utc) - timedelta(days=1)

    g.current_patrons = [patron1, patron2]


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
        g.current_user.return_book(g.current_book.id)
    except ValidationError as exc:
        g.current_exception = exc


@when("the system processes the overdue checkouts")
def process_overdue_checkouts():
    from protean.globals import g

    DailySheetService(patrons=g.current_patrons).run()


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


@then("the checkout statuses are updated to overdue")
def confirm_overdue_marking():
    from protean.globals import g

    assert g.current_patrons[0].checkouts[0].status == "OVERDUE"
    assert g.current_patrons[1].checkouts[0].status == "OVERDUE"
    assert hasattr(g, "current_exception") is False
