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
from app.models import Lesson, PracticeProblem, Subject


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
        python = Subject(
                    name="Python",
                    slug="python",
                    category="Programming",
                    description="Python path",
                    difficulty="beginner",
                    estimated_minutes=60,
                )
        react = Subject(
                    name="React",
                    slug="react",
                    category="Web development",
                    description="React path",
                    difficulty="beginner",
                    estimated_minutes=60,
                )
        session.add_all([python, react])
        session.flush()
        session.add_all([
            Lesson(
                subject_id=python.id, title="Python foundations", slug="python-foundations",
                summary="Variables and values", content="Build your first Python programs.",
                code_example="print('hello')", order_index=1, estimated_minutes=30,
            ),
            PracticeProblem(
                title="Two Sum", slug="two-sum", description="Find a pair.",
                difficulty="Easy", category="Arrays", acceptance_rate=48,
            ),
        ])
        session.commit()

    def override_get_db() -> Generator[Session, None, None]:
        with session_factory() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
