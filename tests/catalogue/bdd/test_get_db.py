from catalogue.main import get_db
from sqlalchemy.orm import Session


def test_get_db():
    db = next(get_db())
    assert db is not None
    assert isinstance(db, Session)
    assert db.bind is not None
    assert db.bind.url.database == "./books.db"
