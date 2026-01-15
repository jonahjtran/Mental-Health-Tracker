import sys
from pathlib import Path

import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker


ROOT_DIR = Path(__file__).resolve().parents[2]
BACKEND_DIR = ROOT_DIR / "backend"
APP_DIR = BACKEND_DIR / "app"
for path in (ROOT_DIR, BACKEND_DIR, APP_DIR):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from backend.app.db.base import Base
from backend.app.db import models
from backend.app.repositories import user_repository


@pytest.fixture()
def db_session() -> Session:
    engine = create_engine("sqlite+pysqlite:///:memory:", future=True)
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
    session = SessionLocal()

    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


def test_create_oauth_user_persists(db_session: Session) -> None:
    user = user_repository.create_oauth_user(
        db_session,
        provider="google",
        subject="sub-123",
        email="ana@example.com",
        name="Ana",
        avatar_url=None,
    )

    assert user.id is not None
    stored = db_session.execute(select(models.Users)).scalars().all()
    assert len(stored) == 1
    assert stored[0].oauth_provider == "google"
    assert stored[0].oauth_subject == "sub-123"


def test_get_user_by_oauth_returns_match(db_session: Session) -> None:
    user = user_repository.create_oauth_user(
        db_session,
        provider="google",
        subject="sub-456",
        email="bea@example.com",
        name="Bea",
        avatar_url="http://avatar.test/1",
    )

    found = user_repository.get_user_by_oauth(db_session, "google", "sub-456")

    assert found is not None
    assert found.id == user.id


def test_link_oauth_identity_updates_user(db_session: Session) -> None:
    user = user_repository.create_oauth_user(
        db_session,
        provider="google",
        subject="sub-old",
        email="cam@example.com",
        name="Cam",
        avatar_url=None,
    )

    updated = user_repository.link_oauth_identity(
        db_session,
        user_id=user.id,
        provider="google",
        subject="sub-new",
        avatar_url="http://avatar.test/2",
    )

    assert updated is not None
    assert updated.oauth_subject == "sub-new"
    assert updated.avatar_url == "http://avatar.test/2"
