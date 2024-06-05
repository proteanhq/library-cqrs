import lending
import os
import pytest

from datetime import timedelta
from faker import Faker

Faker.seed(0)
fake = Faker()


def pytest_addoption(parser):
    parser.addoption(
        "--env",
        action="store",
        default="TESTING",
        help="Config environment to run tests on",
    )


def pytest_sessionstart(session):
    """Pytest hook to run before collecting tests.

    Fetch and activate the domain by pushing the associated domain_context. The activated domain can then be referred to elsewhere as `current_domain`
    """
    os.environ["PROTEAN_ENV"] = session.config.option.env

    from lending.domain import lending

    lending.domain_context().push()
    lending.init()


@pytest.fixture(autouse=True)
def run_around_tests():
    """Fixture to automatically cleanup infrastructure after every test"""
    yield

    from protean.globals import current_domain

    # Clear all databases
    for _, provider in current_domain.providers.items():
        provider._data_reset()

    # Drain event stores
    current_domain.event_store.store._data_reset()


############
# FIXTURES #
############


@pytest.fixture
def patron():
    return lending.Patron()


@pytest.fixture
def regular_patron(patron):
    patron.patron_type = lending.PatronType.REGULAR.value
    return patron


@pytest.fixture
def researcher_patron(patron):
    patron.patron_type = lending.PatronType.RESEARCHER.value
    return patron


@pytest.fixture
def overdue_checkouts_patron(patron):
    checkout_date1 = fake.date_time_between(start_date="-90d", end_date="-61d")
    checkout_date2 = fake.date_time_between(start_date="-80d", end_date="-71d")
    checkout_date3 = fake.date_time_between(start_date="-85d", end_date="-75d")
    patron.checkouts = [
        lending.Checkout(
            branch_id="1",
            book_id=fake.uuid4(),
            checkout_date=checkout_date1,
            due_date=checkout_date1 + timedelta(days=60),
        ),
        lending.Checkout(
            branch_id="1",
            book_id=fake.uuid4(),
            checkout_date=checkout_date2,
            due_date=checkout_date2 + timedelta(days=60),
        ),
        lending.Checkout(
            branch_id="1",
            book_id=fake.uuid4(),
            checkout_date=checkout_date3,
            due_date=checkout_date3 + timedelta(days=60),
        ),
    ]
    return patron


@pytest.fixture
def book():
    return lending.Book(
        isbn=fake.isbn13(),
    )


@pytest.fixture
def five_books():
    return [lending.Book(isbn=fake.isbn13()) for _ in range(5)]


@pytest.fixture
def circulating_book(book):
    book.book_type = lending.BookType.CIRCULATING.value
    return book


@pytest.fixture
def restricted_book(book):
    book.book_type = lending.BookType.RESTRICTED.value
    return book
