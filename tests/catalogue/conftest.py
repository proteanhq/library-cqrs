import pytest
from catalogue.database import (
    Base,
    SessionLocal,
    engine,
)
from sqlalchemy import text
from sqlalchemy.orm import clear_mappers


# Session-level fixture for database setup and teardown
@pytest.fixture(scope="session", autouse=True)
def setup_database():
    # Create all tables at the start of the session
    Base.metadata.create_all(bind=engine)
    yield
    # Drop all tables at the end of the session
    Base.metadata.drop_all(bind=engine)
    clear_mappers()


# Function-level fixture for clearing database records
@pytest.fixture(scope="function")
def db_session():
    session = SessionLocal()
    yield session
    session.close()
    # Clear all data after each test
    with engine.connect() as connection:
        for table in reversed(Base.metadata.sorted_tables):
            connection.execute(text(f"DELETE FROM {table.name}"))
            connection.commit()


# Function-level fixture for TestClient with database session override
@pytest.fixture(scope="function")
def client(db_session):
    from catalogue.main import app, get_db  # Adjust the import path as needed
    from fastapi.testclient import TestClient

    def override_get_db():
        try:
            yield db_session
        finally:
            db_session.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
