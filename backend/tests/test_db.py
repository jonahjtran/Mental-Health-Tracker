import sys
from pathlib import Path
from datetime import date

import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker, Session



# Ensure the repository root is on the import path when pytest runs from subdirectories.
ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from backend.app.db.base import Base
from backend.app.db import models


@pytest.fixture()
def db_session() -> Session:
    """Create a fresh in-memory SQLite database for every test."""
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


def test_create_user_persists(db_session: Session) -> None:
    user = models.Users(name="Alice", email="alice@example.com")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    assert user.id is not None
    stored = db_session.get(models.Users, user.id)
    assert stored is not None
    assert stored.name == "Alice"
    assert stored.email == "alice@example.com"
    assert stored.journal_entries == []


def test_journal_entry_relationship(db_session: Session) -> None:
    user = models.Users(name="Bob", email="bob@example.com")
    entry = models.Journal(
        user=user,
        date=date(2024, 1, 1),
        mood_rating=4,
        entry="Feeling optimistic today",
    )
    db_session.add(entry)
    db_session.commit()

    reloaded_user = db_session.execute(
        select(models.Users).where(models.Users.email == "bob@example.com")
    ).scalar_one()
    assert len(reloaded_user.journal_entries) == 1
    assert reloaded_user.journal_entries[0].entry == "Feeling optimistic today"
    assert reloaded_user.journal_entries[0].user_id == reloaded_user.id


def test_deleting_user_cascades_to_journals(db_session: Session) -> None:
    user = models.Users(name="Cara", email="cara@example.com")
    user.journal_entries = [
        models.Journal(date=date(2024, 2, 1), mood_rating=2, entry="Rough day"),
        models.Journal(date=date(2024, 2, 2), mood_rating=5, entry="Better now"),
    ]
    db_session.add(user)
    db_session.commit()

    db_session.delete(user)
    db_session.commit()

    remaining_journals = db_session.execute(select(models.Journal)).scalars().all()
    assert remaining_journals == []
