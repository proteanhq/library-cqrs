from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.orm import relationship

from .database import Base


class Book(Base):
    __tablename__ = "books"

    isbn = Column(String(13), primary_key=True, index=True)
    title = Column(String(255), nullable=False, index=True)
    summary = Column(Text)
    price = Column(Float, nullable=False)

    instances = relationship("BookInstance", back_populates="book")


class BookInstance(Base):
    __tablename__ = "book_instances"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    isbn = Column(String(13), ForeignKey("books.isbn"), nullable=False)
    is_circulating = Column(Boolean, default=True)
    added_at = Column(DateTime, server_default=func.now())

    book = relationship("Book", back_populates="instances")
