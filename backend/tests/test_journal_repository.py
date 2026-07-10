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
from backend.app.repositories.journal_repository import (
    create_journal,
    delete_journal,
    get_journal_by_id,
    get_journals_by_date,
    get_journals_by_mood_rating,
    get_journals_by_mood_rating_and_date,
    get_journals_by_user,
    get_journals_in_range,
    update_journal,
)
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


def test_create_and_get_journal_by_id_returns_correct_entry(db_session: Session) -> None:
    user = _create_user(db_session, "Maya", "maya@example.com")
    first = create_journal(
        db_session,
        user.id,
        JournalCreate(date=date(2024, 3, 1), mood_rating=2, entry="Not great."),
    )
    second = create_journal(
        db_session,
        user.id,
        JournalCreate(date=date(2024, 3, 2), mood_rating=4, entry="Better."),
    )

    fetched = get_journal_by_id(db_session, second.id)

    assert fetched is not None
    assert fetched.id == second.id
    assert fetched.entry == "Better."
    assert fetched.id != first.id


def test_get_journals_filters_by_user_date_and_rating(db_session: Session) -> None:
    user = _create_user(db_session, "Lee", "lee@example.com")
    other_user = _create_user(db_session, "Omar", "omar@example.com")

    create_journal(
        db_session,
        user.id,
        JournalCreate(date=date(2024, 4, 1), mood_rating=5, entry="Great day."),
    )
    create_journal(
        db_session,
        user.id,
        JournalCreate(date=date(2024, 4, 2), mood_rating=3, entry="Average."),
    )
    create_journal(
        db_session,
        other_user.id,
        JournalCreate(date=date(2024, 4, 1), mood_rating=5, entry="Different user."),
    )

    by_user = get_journals_by_user(db_session, user.id)
    assert len(by_user) == 2

    by_date = get_journals_by_date(db_session, user.id, date(2024, 4, 1))
    assert len(by_date) == 1
    assert by_date[0].entry == "Great day."

    by_rating = get_journals_by_mood_rating(db_session, user.id, 5)
    assert len(by_rating) == 1
    assert by_rating[0].entry == "Great day."

    by_rating_and_date = get_journals_by_mood_rating_and_date(
        db_session, user.id, 5, date(2024, 4, 1)
    )
    assert len(by_rating_and_date) == 1
    assert by_rating_and_date[0].entry == "Great day."


def test_update_journal_persists_changes(db_session: Session) -> None:
    user = _create_user(db_session, "Sam", "sam@example.com")
    journal = create_journal(
        db_session,
        user.id,
        JournalCreate(date=date(2024, 5, 1), mood_rating=1, entry="Tough start."),
    )

    updated = update_journal(
        db_session,
        journal.id,
        JournalUpdate(date=date(2024, 5, 2), mood_rating=4, entry="Improved."),
    )

    assert updated is not None
    assert updated.mood_rating == 4
    assert updated.entry == "Improved."


def test_get_journals_in_range_filters_by_user_and_dates(db_session: Session) -> None:
    user = _create_user(db_session, "Ivy", "ivy@example.com")
    other_user = _create_user(db_session, "Jon", "jon@example.com")

    create_journal(
        db_session,
        user.id,
        JournalCreate(date=date(2024, 4, 1), mood_rating=3, entry="In range start."),
    )
    create_journal(
        db_session,
        user.id,
        JournalCreate(date=date(2024, 4, 10), mood_rating=4, entry="In range end."),
    )
    create_journal(
        db_session,
        user.id,
        JournalCreate(date=date(2024, 4, 20), mood_rating=5, entry="Out of range."),
    )
    create_journal(
        db_session,
        other_user.id,
        JournalCreate(date=date(2024, 4, 5), mood_rating=2, entry="Different user."),
    )

    result = get_journals_in_range(db_session, user.id, date(2024, 4, 1), date(2024, 4, 10))

    assert [j.entry for j in result] == ["In range start.", "In range end."]


def test_delete_journal_removes_entry(db_session: Session) -> None:
    user = _create_user(db_session, "Noah", "noah@example.com")
    journal = create_journal(
        db_session,
        user.id,
        JournalCreate(date=date(2024, 6, 1), mood_rating=3, entry="Steady."),
    )

    result = delete_journal(db_session, journal.id)

    assert result is True
    remaining = db_session.execute(select(models.Journal)).scalars().all()
    assert remaining == []
