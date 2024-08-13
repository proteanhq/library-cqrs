import pytest
from protean import current_domain, g
from pytest_bdd import given, then, when

from lending import Book, BookStatus, HoldType, PlaceHold


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


@given("a regular patron is logged in")
def a_regular_patron_is_logged_in(regular_patron):
    g.current_user = regular_patron


@when("the patron places a hold on the book")
def the_patron_places_a_hold_on_the_book():
    command = PlaceHold(
        patron_id=g.current_user.id,
        book_id=g.current_book.id,
        branch_id="1",
        hold_type=HoldType.CLOSED_ENDED.value,
    )
    current_domain.process(command)


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
