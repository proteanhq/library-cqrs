from pytest_bdd import given, when, then, scenario
from pytest_bdd.parsers import cfparse

from lending.holding_service import HoldingService


@scenario('../features/place_a_hold_on_a_book.feature', 'Regular patron places a hold on an available circulating book')
def test_regular_patron_places_a_hold_on_an_available_circulating_book():
    pass

@given("a circulating book is available", target_fixture="circulating_book_instance")
def circulating_book_instance(book):
    from protean.globals import g
    g.current_book_instance = book.book_instances[0]


@given(cfparse('a restricted book is available'), target_fixture="restricted_book_instance")
def restricted_book_instance(book):
    from protean.globals import g
    g.current_book_instance = book.book_instances[1]


@given("a regular patron is logged in", target_fixture="regular_patron")
def regular_patron(regular_patron):
    from protean.globals import g
    g.current_user = regular_patron


@given('a researcher patron is logged in', target_fixture="researcher_patron")
def researcher_patron(researcher_patron):
    from protean.globals import g
    g.current_user = researcher_patron


@when("the patron places a hold on the book")
def place_hold():
    from protean.globals import g
    HoldingService(g.current_user,  g.current_book_instance).place_hold()


@then("the hold is successfully placed")
def hold_placed():
    from protean.globals import g
    patron = g.current_user
    assert len(patron.holds) == 1
    assert patron.holds[0].book_instance_id == g.current_book_instance.id
