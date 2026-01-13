import sys
from pathlib import Path
from datetime import date

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
from backend.app.services.journal_services import (
    create_journal_entry,
    delete_journal_entry,
    get_journal_by_id,
    list_journal_entries,
    update_journal_entry,
)
from backend.app.services.errors import NotFoundError
from backend.app.schemas.journal import JournalCreate, JournalUpdate


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
    payload = JournalCreate(
        date=date(2024, 7, 1),
        mood_rating=4,
        entry="Feeling good.",
    )

    result = create_journal_entry(db_session, user.id, payload)

    assert result is not None
    assert result.user_id == user.id
    stored = db_session.execute(select(models.Journal)).scalars().all()
    assert len(stored) == 1
    assert stored[0].entry == "Feeling good."

def test_delete_journal_entry_missing_raises(db_session: Session) -> None:
    user = _create_user(db_session, "Nia", "nia@example.com")
    with pytest.raises(NotFoundError):
        delete_journal_entry(db_session, user.id, 999)


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

    result = delete_journal_entry(db_session, user.id, journal.id)

    assert result is not None
    assert result.id == journal.id
    remaining = db_session.execute(select(models.Journal)).scalars().all()
    assert remaining == []


def test_update_journal_entry_updates_row(db_session: Session) -> None:
    user = _create_user(db_session, "Wes", "wes@example.com")
    journal = models.Journal(
        user_id=user.id,
        date=date(2024, 7, 5),
        mood_rating=2,
        entry="Before.",
    )
    db_session.add(journal)
    db_session.commit()

    payload = JournalUpdate(entry="After.", mood_rating=5)
    result = update_journal_entry(db_session, user.id, journal.id, payload)

    assert result is not None
    assert result.entry == "After."
    assert result.mood_rating == 5


def test_update_journal_entry_missing_raises(db_session: Session) -> None:
    user = _create_user(db_session, "Ola", "ola@example.com")
    payload = JournalUpdate(entry="Nope.")

    with pytest.raises(NotFoundError):
        update_journal_entry(db_session, user.id, 999, payload)


def test_get_journal_by_id_enforces_user(db_session: Session) -> None:
    user = _create_user(db_session, "Zoe", "zoe@example.com")
    other = _create_user(db_session, "Ana", "ana@example.com")
    journal = models.Journal(
        user_id=user.id,
        date=date(2024, 7, 6),
        mood_rating=3,
        entry="Scoped.",
    )
    db_session.add(journal)
    db_session.commit()

    assert get_journal_by_id(db_session, user.id, journal.id) is not None
    with pytest.raises(NotFoundError):
        get_journal_by_id(db_session, other.id, journal.id)


def test_list_journal_entries_missing_user_raises(db_session: Session) -> None:
    with pytest.raises(NotFoundError):
        list_journal_entries(db_session, 999)
