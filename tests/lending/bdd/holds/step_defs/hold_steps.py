import pytest

from datetime import datetime, timedelta

from pytest_bdd import given, when, then

from protean.exceptions import ValidationError

from lending import BookStatus, BookType, HoldingService, HoldType, HoldStatus, DailySheetService


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


@given("a regular patron is logged in")
@given("a patron is logged in")
def regular_patron(regular_patron):
    from protean.globals import g

    g.current_user = regular_patron


@given("a researcher patron is logged in")
def a_researcher_patron(researcher_patron):
    from protean.globals import g

    g.current_user = researcher_patron


@given("a book is already on hold by another patron")
def already_held_book(book):
    from protean.globals import g

    book.status = BookStatus.ON_HOLD.value
    g.current_book = book


@given("a patron has more than two overdue checkouts at the branch")
def more_than_two_overdue_checkouts(overdue_checkouts_patron, book):
    from protean.globals import g

    g.current_user = overdue_checkouts_patron
    g.current_book = book


@given('a closed-ended hold is placed')
def closed_ended_hold_placed():
    from protean.globals import g
    HoldingService(
        g.current_user, g.current_book, "1", HoldType.CLOSED_ENDED
    ).place_hold()


@given('the hold has reached its expiry date')
def hold_expired():
    from protean.globals import g
    g.current_user.holds[0].expiry_date = datetime.now() - timedelta(days=1)


@given('patron has fewer than five holds')
def patron_with_fewer_than_five_holds():
    from protean.globals import g
    assert len(g.current_user.holds) < 5


@given('patron has exactly five holds')
def patron_with_exactly_five_holds(five_books):
    from protean.globals import g

    for i in range(5 - len(g.current_user.holds)):
        HoldingService(
            g.current_user, five_books[i], "1", HoldType.CLOSED_ENDED
        ).place_hold()
    assert len(g.current_user.holds) == 5



@given('a patron has an active hold')
def patron_with_active_hold(patron, book):
    from protean.globals import g

    g.current_user = patron
    g.current_book = book

    HoldingService(g.current_user, book, "1", HoldType.CLOSED_ENDED).place_hold()


@given('a patron has an expired hold')
def patron_with_expired_hold(patron, book):
    from protean.globals import g

    g.current_user = patron
    g.current_book = book

    HoldingService(g.current_user, book, "1", HoldType.CLOSED_ENDED).place_hold()
    g.current_user.holds[0].expiry_date = datetime.now() - timedelta(days=1)


@given('a patron has a hold that has been checked out')
def patron_with_checked_out_hold(patron, book):
    from protean.globals import g

    g.current_user = patron
    g.current_book = book

    HoldingService(g.current_user, book, "1", HoldType.CLOSED_ENDED).place_hold()
    g.current_user.holds[0].status = HoldStatus.CHECKED_OUT.value


@when("the patron places a hold on the book")
@when("the patron tries to place a hold on the book")
@when("the patron tries to place a hold on a book")
@when("the patron tries to place an additional hold")
def place_hold():
    from protean.globals import g

    try:
        HoldingService(g.current_user, g.current_book,"1", HoldType.CLOSED_ENDED).place_hold()
    except ValidationError as exc:
        g.current_exception = exc


@when('the patron places an open-ended hold')
@when("the patron tries to place an open-ended hold")
def place_open_ended_hold():
    from protean.globals import g

    try:
        HoldingService(
            g.current_user, g.current_book, "1", HoldType.OPEN_ENDED
        ).place_hold()
    except ValidationError as exc:
        g.current_exception = exc


@when("the patron places a closed-ended hold")
def closed_ended_hold():
    from protean.globals import g

    try:
        HoldingService(
            g.current_user, g.current_book, "1", HoldType.CLOSED_ENDED
        ).place_hold()
    except ValidationError as exc:
        g.current_exception = exc


@when('the system checks for expiring holds')
def check_expiring_holds():
    from protean.globals import g
    DailySheetService(patrons=[g.current_user]).run()


@when('the patron places more than five holds')
def place_more_than_five_holds(five_books):
    from protean.globals import g
    for i in range(5):
        HoldingService(
            g.current_user, five_books[i], "1", HoldType.CLOSED_ENDED
        ).place_hold()
    
    # Place one more hold
    HoldingService(
            g.current_user, g.current_book, "1", HoldType.CLOSED_ENDED
        ).place_hold()


@when('the patron cancels the hold')
@when('the patron tries to cancel the hold')
def cancel_hold():
    from protean.globals import g
    patron = g.current_user

    try:
        patron.cancel(patron.holds[0])
    except ValidationError as exc:
        g.current_exception = exc


@then("the hold is successfully placed")
def hold_placed():
    from protean.globals import g

    patron = g.current_user
    assert len(patron.holds) == 1
    assert patron.holds[0].book_id == g.current_book.id
    assert hasattr(g, "current_exception") is False


@then("all holds are successfully placed")
def holds_placed(five_books):
    from protean.globals import g

    patron = g.current_user
    assert len(patron.holds) == 6
    assert patron.holds[0].book_id == five_books[0].id
    assert patron.holds[5].book_id == g.current_book.id
    assert hasattr(g, "current_exception") is False


@then("the hold placement is rejected")
def hold_rejected():
    from protean.globals import g

    assert hasattr(g, "current_exception")
    assert isinstance(g.current_exception, ValidationError)


@then('the hold status is updated to expired')
def check_hold_expired():
    from protean.globals import g

    assert g.current_user.holds[0].status == HoldStatus.EXPIRED.value


@then('the hold is successfully canceled')
def check_hold_canceled():
    from protean.globals import g

    assert g.current_user.holds[0].status == HoldStatus.CANCELLED.value


@then('the cancellation is rejected')
def check_hold_cancellation_rejected():
    from protean.globals import g

    assert hasattr(g, "current_exception")
    assert isinstance(g.current_exception, ValidationError)
