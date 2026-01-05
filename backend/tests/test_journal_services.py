import sys
from pathlib import Path
from datetime import date

import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker
from typing import Optional


ROOT_DIR = Path(__file__).resolve().parents[2]
BACKEND_DIR = ROOT_DIR / "backend"
APP_DIR = BACKEND_DIR / "app"
for path in (ROOT_DIR, BACKEND_DIR, APP_DIR):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from backend.app.db.base import Base
from backend.app.db import models
from backend.app.services.journal_services import (
    create_journal_entry,
    delete_journal_entry,
)


class JournalPayload:
    def __init__(
        self,
        user_id: int,
        date_value: Optional[date],
        mood_rating: Optional[int],
        entry: Optional[str],
    ) -> None:
        self.user_id = user_id
        self.date = date_value
        self.mood_rating = mood_rating
        self.entry = entry


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


def _create_user(db_session: Session, name: str, email: str) -> models.Users:
    user = models.Users(name=name, email=email)
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


def test_create_journal_entry_persists_row(db_session: Session) -> None:
    user = _create_user(db_session, "Rosa", "rosa@example.com")
    payload = JournalPayload(
        user_id=user.id,
        date_value=date(2024, 7, 1),
        mood_rating=4,
        entry="Feeling good.",
    )

    result = create_journal_entry(db_session, user.id, payload)

    assert result is True
    stored = db_session.execute(select(models.Journal)).scalars().all()
    assert len(stored) == 1
    assert stored[0].entry == "Feeling good."


def test_create_journal_entry_rejects_mismatched_user(db_session: Session) -> None:
    user = _create_user(db_session, "Tess", "tess@example.com")
    payload = JournalPayload(
        user_id=user.id + 1,
        date_value=date(2024, 7, 2),
        mood_rating=3,
        entry="Neutral.",
    )

    result = create_journal_entry(db_session, user.id, payload)

    assert result[0] is False
    assert "User ID" in result[1]
    stored = db_session.execute(select(models.Journal)).scalars().all()
    assert stored == []


def test_create_journal_entry_rejects_invalid_rating(db_session: Session) -> None:
    user = _create_user(db_session, "Uma", "uma@example.com")
    payload = JournalPayload(
        user_id=user.id,
        date_value=date(2024, 7, 3),
        mood_rating=0,
        entry="Too low.",
    )

    result = create_journal_entry(db_session, user.id, payload)

    assert result[0] is False
    assert "Mood rating" in result[1]
    stored = db_session.execute(select(models.Journal)).scalars().all()
    assert stored == []


def test_delete_journal_entry_missing_returns_false(db_session: Session) -> None:
    result = delete_journal_entry(db_session, 999)

    assert result[0] is False
    assert "does not exist" in result[1]


def test_delete_journal_entry_removes_row(db_session: Session) -> None:
    user = _create_user(db_session, "Vera", "vera@example.com")
    journal = models.Journal(
        user_id=user.id,
        date=date(2024, 7, 4),
        mood_rating=5,
        entry="Great!",
    )
    db_session.add(journal)
    db_session.commit()

    result = delete_journal_entry(db_session, journal.id)

    assert result is True
    remaining = db_session.execute(select(models.Journal)).scalars().all()
    assert remaining == []
