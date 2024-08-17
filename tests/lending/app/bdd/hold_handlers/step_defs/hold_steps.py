import pytest
from protean import current_domain, g
from protean.exceptions import ValidationError
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


@when("the patron places a hold on the book")
@when("the patron tries to place a hold on the book")
@when("the patron tries to place a hold on a book")
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
def the_hold_placement_is_rejected():
    assert hasattr(g, "current_exception")
    assert isinstance(g.current_exception, ValidationError)


@then("the book is not marked as held")
def the_book_is_not_marked_as_held():
    book = current_domain.repository_for(Book).get(g.current_book.id)
    assert book.status != BookStatus.ON_HOLD.value
