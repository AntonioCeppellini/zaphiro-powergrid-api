from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.session import close_all_sessions

import app.models
from app.db.base import Base
from app.main import app
from app.db.connection import get_db
from app.tests.config import TEST_DATABASE_URL
from app.tests.utils import TestDatabase


def _db_name(test_url: str) -> str:
    return make_url(test_url).database


@pytest.fixture(scope="session", autouse=True)
def create_and_delete_database():
    test_db_name = _db_name(TEST_DATABASE_URL)
    postgres_url = make_url(TEST_DATABASE_URL)

    engine = create_engine(TEST_DATABASE_URL, pool_pre_ping=True)
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    TestDatabase(session=SessionLocal()).populate_test_database()

    yield

    close_all_sessions()
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture(scope="function")
def db():
    engine = create_engine(TEST_DATABASE_URL, pool_pre_ping=True)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    yield SessionLocal()


@pytest.fixture(scope="function")
def client():
    # override app DB dependency to always use TEST_DATABASE_URL
    engine = create_engine(TEST_DATABASE_URL, pool_pre_ping=True)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    def _override_get_db():
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = _override_get_db

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()
    engine.dispose()
