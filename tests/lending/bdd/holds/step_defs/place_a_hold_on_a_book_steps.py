import pytest

from pytest_bdd import given, when, then
from pytest_bdd.parsers import cfparse

from protean.exceptions import ValidationError

from lending import BookStatus, BookType, HoldingService


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
def circulating_book_instance(book):
    from protean.globals import g
    g.current_book = book


@given(cfparse('a restricted book is available'))
def restricted_book_instance(book):
    from protean.globals import g
    book.book_type = BookType.RESTRICTED.value
    g.current_book = book


@given("a regular patron is logged in")
@given('a patron is logged in')
def regular_patron(regular_patron):
    from protean.globals import g
    g.current_user = regular_patron


@given('a researcher patron is logged in')
def a_researcher_patron(researcher_patron):
    from protean.globals import g
    g.current_user = researcher_patron


@given('a book is already on hold by another patron')
def already_held_book(book):
    from protean.globals import g
    book.status = BookStatus.ON_HOLD.value
    g.current_book = book


@given('a patron has more than two overdue checkouts at the branch')
def more_than_two_overdue_checkouts(overdue_checkouts_patron, book):
    from protean.globals import g
    g.current_user = overdue_checkouts_patron
    g.current_book = book


@when("the patron places a hold on the book")
@when("the patron tries to place a hold on the book")
@when("the patron tries to place a hold on a book")
def place_hold():
    from protean.globals import g
    try:
        HoldingService(g.current_user,  g.current_book, "1").place_hold()
    except ValidationError as exc:
        g.current_exception = exc


@then("the hold is successfully placed")
def hold_placed():
    from protean.globals import g
    patron = g.current_user
    assert len(patron.holds) == 1
    assert patron.holds[0].book_id == g.current_book.id


@then('the hold placement is rejected')
def hold_rejected():
    from protean.globals import g
    assert hasattr(g, "current_exception")
    assert isinstance(g.current_exception, ValidationError)
