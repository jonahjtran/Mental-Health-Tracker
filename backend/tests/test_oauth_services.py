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
from backend.app.services import users_services


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


def _create_local_user(db_session: Session, email: str) -> models.Users:
    user = models.Users(
        name="Local User",
        email=email,
        oauth_provider="local",
        oauth_subject=f"local:{email}",
        avatar_url=None,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


def test_get_or_create_user_from_oauth_existing_identity(db_session: Session) -> None:
    existing = user_repository.create_oauth_user(
        db_session,
        provider="google",
        subject="sub-existing",
        email="dee@example.com",
        name="Dee",
        avatar_url=None,
    )

    result = users_services.get_or_create_user_from_oauth(
        db_session,
        provider="google",
        subject="sub-existing",
        email="dee@example.com",
        name="Dee",
        avatar_url=None,
    )

    assert result.id == existing.id
    stored = db_session.execute(select(models.Users)).scalars().all()
    assert len(stored) == 1


def test_get_or_create_user_from_oauth_links_by_email(db_session: Session) -> None:
    local = _create_local_user(db_session, "eve@example.com")

    linked = users_services.get_or_create_user_from_oauth(
        db_session,
        provider="google",
        subject="sub-linked",
        email="eve@example.com",
        name="Eve",
        avatar_url="http://avatar.test/3",
    )

    assert linked.id == local.id
    assert linked.oauth_provider == "google"
    assert linked.oauth_subject == "sub-linked"
    assert linked.avatar_url == "http://avatar.test/3"


def test_get_or_create_user_from_oauth_creates_new(db_session: Session) -> None:
    created = users_services.get_or_create_user_from_oauth(
        db_session,
        provider="google",
        subject="sub-new",
        email="fin@example.com",
        name="Fin",
        avatar_url=None,
    )

    assert created.id is not None
    assert created.email == "fin@example.com"
    stored = db_session.execute(select(models.Users)).scalars().all()
    assert len(stored) == 1
