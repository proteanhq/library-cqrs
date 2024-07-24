import pytest
from catalogue.main import BookInstanceRequest, BookRequest
from catalogue.models import Book, BookInstance
from pytest_bdd import given, then, when
from sqlalchemy.exc import IntegrityError


@pytest.fixture
def book_data():
    return BookRequest(
        isbn="1234567890123",
        title="Test Book",
        summary="This is a test book",
        price=9.99,
    )


@pytest.fixture
def book_instance_data():
    return BookInstanceRequest(
        isbn="1234567890123",
        is_circulating=True,
    )


@given("a book exists in the catalogue")
def add_book_to_catalogue(db_session, book_data):
    book = Book(**book_data.model_dump())
    db_session.add(book)
    db_session.commit()


@given("no book exists with the provided ISBN")
def no_book_exists_with_provided_isbn(db_session, book_data):
    pass


@when("the librarian adds a new book with valid details")
def add_new_book_with_valid_details(client, book_data):
    # Test creating a book
    response = client.post("/book", json=book_data.model_dump())
    assert response.status_code == 201
    assert response.json() == {"message": "Book added successfully"}


@when("the librarian tries to add a book with a missing price")
def add_new_book_with_missing_price(client, book_data):
    del book_data.price
    response = client.post("/book", json=book_data.model_dump())
    assert response.status_code == 422
    assert response.json() == {
        "detail": [
            {
                "type": "missing",
                "loc": ["body", "price"],
                "msg": "Field required",
                "input": {
                    "isbn": "1234567890123",
                    "title": "Test Book",
                    "summary": "This is a test book",
                },
            }
        ]
    }


@when("the librarian tries to add a book with an empty title")
def add_new_book_with_empty_title(client, book_data):
    book_data.title = ""
    response = client.post("/book", json=book_data.model_dump())
    assert response.status_code == 422
    assert response.json() == {
        "detail": [
            {
                "type": "string_too_short",
                "loc": ["body", "title"],
                "msg": "String should have at least 1 character",
                "input": "",
                "ctx": {"min_length": 1},
            }
        ]
    }


@when("the librarian adds a circulating book instance")
def add_circulating_book_instance(client, book_instance_data):
    response = client.post("/book_instance", json=book_instance_data.model_dump())
    assert response.status_code == 201
    assert response.json() == {"message": "Book instance added successfully"}


@when("the librarian tries to add a book instance")
def add_book_instance(client, book_instance_data):
    try:
        client.post("/book_instance", json=book_instance_data.model_dump())
    except IntegrityError as e:
        assert e.args[0] == "(sqlite3.IntegrityError) FOREIGN KEY constraint failed"


@when("the librarian adds a restricted book instance")
def add_restricted_book_instance(client, book_instance_data):
    book_instance_data.is_circulating = False
    response = client.post("/book_instance", json=book_instance_data.model_dump())
    assert response.status_code == 201
    assert response.json() == {"message": "Book instance added successfully"}


@then("the book is successfully added to the catalogue")
def verify_book_added_to_catalogue(db_session, book_data):
    # Verify that the book is added to the database
    book = db_session.query(Book).filter_by(isbn=book_data.isbn).first()
    assert book is not None
    assert book.title == book_data.title
    assert book.summary == book_data.summary
    assert book.price == book_data.price


@then("the book is not added to the catalogue")
def verify_book_not_added_to_catalogue(db_session, book_data):
    # Verify that the book is not added to the database
    book = db_session.query(Book).filter_by(isbn=book_data.isbn).first()
    assert book is None


@then("the book instance is successfully added to the catalogue")
def verify_book_instance_added_to_catalogue(db_session, book_data):
    # Verify that the book instance is added to the database
    book_instance = (
        db_session.query(BookInstance).filter_by(isbn=book_data.isbn).first()
    )
    assert book_instance is not None


@then("the book instance is not added to the catalogue")
def verify_book_instance_not_added_to_catalogue(db_session, book_data):
    # Verify that the book instance is not added to the database
    book_instance = (
        db_session.query(BookInstance).filter_by(isbn=book_data.isbn).first()
    )
    assert book_instance is None
