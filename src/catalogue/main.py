import json
from typing import Annotated

import redis
from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from starlette import status

from .database import Base, SessionLocal, engine
from .models import Book, BookInstance

app = FastAPI()


Base.metadata.create_all(bind=engine)


# Redis setup
def get_redis_client():
    return redis.Redis(host="localhost", port=6379, db=0)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]


class BookRequest(BaseModel):
    isbn: str = Field(min_length=13, max_length=13)
    title: str = Field(min_length=1, max_length=255)
    summary: str = Field(max_length=1024)
    price: float = Field(gt=0)


# Pydantic model for a book instance
class BookInstanceRequest(BaseModel):
    isbn: str = Field(min_length=13, max_length=13)
    is_circulating: bool = Field(default=True)


@app.post("/book", status_code=status.HTTP_201_CREATED)
async def add_book(db: db_dependency, book_request: BookRequest):
    new_book = Book(**book_request.model_dump())

    db.add(new_book)
    db.commit()
    return {"message": "Book added successfully"}


# Add a book instance to the catalogue
@app.post("/book_instance", status_code=status.HTTP_201_CREATED)
async def add_book_instance(
    db: db_dependency,
    book_instance_request: BookInstanceRequest,
    redis_client: redis.Redis = Depends(get_redis_client),
):
    # Check if the book exists
    book = db.query(Book).filter(Book.isbn == book_instance_request.isbn).first()
    if not book:
        raise HTTPException(status_code=400, detail="Book does not exist")

    new_book_instance = BookInstance(**book_instance_request.model_dump())

    db.add(new_book_instance)
    db.commit()

    # Raise Event
    event_dict = {
        "instance_id": new_book_instance.id,
        "isbn": new_book_instance.isbn,
        "title": new_book_instance.book.title,
        "summary": new_book_instance.book.summary,
        "price": new_book_instance.book.price,
        "is_circulating": new_book_instance.is_circulating,
        "added_at": new_book_instance.added_at.isoformat(),
    }
    redis_client.rpush("book_instance_added", json.dumps(event_dict))

    return {"message": "Book instance added successfully"}
