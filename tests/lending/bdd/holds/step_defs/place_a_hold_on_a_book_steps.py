from pytest_bdd import given, when, then, scenario
from pytest_bdd.parsers import cfparse

from lending.holding_service import HoldingService


@scenario('../features/place_a_hold_on_a_book.feature', 'Regular patron places a hold on an available circulating book')
def test_regular_patron_places_a_hold_on_an_available_circulating_book():
    pass

@given(cfparse("a circulating book is available"), target_fixture="a_circulating_book")
def a_circulating_book(circulating_book):
    return circulating_book


@given(cfparse("a regular patron is logged in"), target_fixture="regular_patron")
def regular_patron(regular_patron):
    from protean.globals import g

    g.current_user = regular_patron


@when(cfparse("the patron places a hold on the book"))
def place_hold(a_circulating_book, regular_patron):
    HoldingService(regular_patron, a_circulating_book, a_circulating_book.book_instances[0]).place_hold()


@then(cfparse("the hold is successfully placed"))
def hold_placed(a_circulating_book, regular_patron):
    assert len(regular_patron.holds) == 1
    assert regular_patron.holds[0].book_instance_id == a_circulating_book.book_instances[0].id
