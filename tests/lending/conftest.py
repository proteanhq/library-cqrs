import os
from datetime import timedelta

import pytest
from faker import Faker
from protean import current_domain

import lending

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

    from protean import current_domain

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
    new_patron = lending.Patron()
    current_domain.repository_for(lending.Patron).add(new_patron)
    return new_patron


@pytest.fixture
def regular_patron(patron):
    patron.patron_type = lending.PatronType.REGULAR.value
    current_domain.repository_for(lending.Patron).add(patron)
    return patron


@pytest.fixture
def researcher_patron(patron):
    patron.patron_type = lending.PatronType.RESEARCHER.value
    current_domain.repository_for(lending.Patron).add(patron)
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
            checked_out_at=checkout_date1,
            due_on=checkout_date1.date() + timedelta(days=60),
        ),
        lending.Checkout(
            branch_id="1",
            book_id=fake.uuid4(),
            checked_out_at=checkout_date2,
            due_on=checkout_date2.date() + timedelta(days=60),
        ),
        lending.Checkout(
            branch_id="1",
            book_id=fake.uuid4(),
            checked_out_at=checkout_date3,
            due_on=checkout_date3.date() + timedelta(days=60),
        ),
    ]
    current_domain.repository_for(lending.Patron).add(patron)
    return patron


@pytest.fixture
def book():
    book = lending.Book(
        isbn=fake.isbn13(),
    )

    current_domain.repository_for(lending.Book).add(book)
    return book


@pytest.fixture
def five_books():
    five_books = [lending.Book(isbn=fake.isbn13()) for _ in range(5)]

    for book in five_books:
        current_domain.repository_for(lending.Book).add(book)

    return five_books


@pytest.fixture
def circulating_book(book):
    book.book_type = lending.BookType.CIRCULATING.value
    current_domain.repository_for(lending.Book).add(book)
    return book


@pytest.fixture
def restricted_book(book):
    book.book_type = lending.BookType.RESTRICTED.value
    current_domain.repository_for(lending.Book).add(book)
    return book
