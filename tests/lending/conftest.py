import lending
import os
import pytest

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
def book():
    return lending.Book(
        isbn=fake.isbn13(),
        title=fake.sentence(nb_words=4),
        price=fake.pyfloat(left_digits=2, right_digits=2),
        book_instances=[
            lending.BookInstance(),
            lending.BookInstance(
                book_instance_type=lending.BookInstanceType.RESTRICTED.value
            ),
        ],
    )
