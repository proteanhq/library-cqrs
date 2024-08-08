from enum import Enum

from protean import UnitOfWork, current_domain, handle
from protean.fields import String

from lending.domain import lending
from lending.model.patron import HoldPlaced


class BookStatus(Enum):
    AVAILABLE = "AVAILABLE"
    ON_HOLD = "ON_HOLD"
    CHECKED_OUT = "CHECKED_OUT"


class BookType(Enum):
    CIRCULATING = "CIRCULATING"
    RESTRICTED = "RESTRICTED"


@lending.aggregate
class Book:
    isbn = String(max_length=25, required=True)
    book_type = String(
        max_length=11,
        required=True,
        choices=BookType,
        default=BookType.CIRCULATING.value,
    )
    status = String(
        max_length=11,
        choices=BookStatus,
        default=BookStatus.AVAILABLE.value,
    )


@lending.repository(part_of=Book)
class BookRepository:
    def find_by_isbn(self, isbn):
        return current_domain.repository_for(Book)._dao.find_by(isbn=isbn)


@lending.event_handler(part_of=Book, stream_category="library::patron")
class PatronHoldEventsHandler:
    @handle(HoldPlaced)
    def mark_book_on_hold(self, event: HoldPlaced):
        repo = lending.repository_for(Book)
        book = repo.get(event.book_id)

        book.status = BookStatus.ON_HOLD.value

        repo.add(book)


@lending.subscriber(channel="book_instance_added")
class AddBookToLibrary:
    def __call__(self, message: dict):
        with UnitOfWork():
            repo = lending.repository_for(Book)

            book_type = (
                BookType.CIRCULATING.value
                if message["is_circulating"]
                else BookType.RESTRICTED.value
            )
            book = Book(
                isbn=message["isbn"],
                book_type=book_type,
                status=BookStatus.AVAILABLE.value,
            )
            repo.add(book)
