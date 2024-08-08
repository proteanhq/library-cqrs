import asyncio

import pytest
from protean import Engine, current_domain
from pytest_bdd import given, then
from pytest_bdd.parsers import cfparse

from lending import Book, BookStatus


@pytest.fixture(autouse=True)
def auto_set_and_close_loop():
    # Create and set a new loop
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    yield

    # Close the loop after the test
    if not loop.is_closed():
        loop.close()
    asyncio.set_event_loop(None)  # Explicitly unset the loop


@given(cfparse("the librarian added a {book_type} book instance"))
def given_the_librarian_added_a_circulating_book_instance(book_type):
    broker = current_domain.brokers["default"]
    broker.publish(
        "book_instance_added",
        {
            "instance_id": 1,
            "isbn": "9783161484100",
            "title": "The Book",
            "summary": "A book about books",
            "price": 10.0,
            "is_circulating": True if book_type == "CIRCULATING" else False,
            "added_at": "2021-01-01T00:00:00Z",
        },
    )

    engine = Engine(current_domain, test_mode=True)
    engine.run()


@then(cfparse("a {book_type} book instance is successfully added as available"))
def then_the_book_instance_is_successfully_added_as_available(book_type):
    book = current_domain.repository_for(Book).find_by_isbn("9783161484100")

    assert book is not None
    assert book.book_type == book_type
    assert book.status == BookStatus.AVAILABLE.value
