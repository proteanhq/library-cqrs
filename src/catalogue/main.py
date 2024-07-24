from typing import Annotated

from fastapi import Depends, FastAPI
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from starlette import status

from .database import Base, SessionLocal, engine
from .models import Book, BookInstance

app = FastAPI()


Base.metadata.create_all(bind=engine)


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
    db: db_dependency, book_instance_request: BookInstanceRequest
):
    new_book_instance = BookInstance(**book_instance_request.model_dump())

    db.add(new_book_instance)
    db.commit()
    return {"message": "Book instance added successfully"}
