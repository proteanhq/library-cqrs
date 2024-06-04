import os
import pytest

from pytest_factoryboy import register

import factories


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


register(factories.PatronFactory)
register(factories.PatronFactory, "regular_patron")
register(factories.ActivePatronFactory, "active_patron")
register(factories.HoldFactory)
register(factories.CheckoutFactory)
register(factories.BookFactory)
register(factories.BookFactory, "circulating_book")
register(factories.BookInstanceFactory)
