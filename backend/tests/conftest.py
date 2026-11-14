import sys
from collections.abc import Generator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

sys.path.insert(0, str(Path(__file__).parents[1]))

from app.db import Base, get_db
from app.main import app
from app.models import Subject


@pytest.fixture()
def client() -> Generator[TestClient, None, None]:
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    session_factory = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
    Base.metadata.create_all(engine)
    with session_factory() as session:
        session.add_all(
            [
                Subject(
                    name="Python",
                    slug="python",
                    category="Programming",
                    description="Python path",
                    difficulty="beginner",
                    estimated_minutes=60,
                ),
                Subject(
                    name="React",
                    slug="react",
                    category="Web development",
                    description="React path",
                    difficulty="beginner",
                    estimated_minutes=60,
                ),
            ],
        )
        session.commit()

    def override_get_db() -> Generator[Session, None, None]:
        with session_factory() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
