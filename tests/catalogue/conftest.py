import pytest
import redis
from catalogue.database import Base
from catalogue.main import app, get_db, get_redis_client
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import clear_mappers, sessionmaker

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


# Create a test-specific Redis client
def override_get_redis_client():
    return redis.Redis(host="localhost", port=6379, db=1)


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
    session = TestingSessionLocal()
    yield session
    session.close()
    # Clear all data after each test
    with engine.connect() as connection:
        for table in reversed(Base.metadata.sorted_tables):
            connection.execute(text(f"DELETE FROM {table.name}"))
            connection.commit()


@pytest.fixture(scope="function")
def redis_session():
    yield
    # Clear the test Redis database after each test
    override_get_redis_client().flushdb()


# Function-level fixture for TestClient with database and redis session override
@pytest.fixture(scope="function")
def client(
    db_session, redis_session
):  # Including these fixtures invokes them after the client fixture
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_redis_client] = override_get_redis_client
    with TestClient(app) as c:
        yield c
