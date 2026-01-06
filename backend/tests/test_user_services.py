import sys
from pathlib import Path
from datetime import date
from typing import Optional

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker


ROOT_DIR = Path(__file__).resolve().parents[2]
BACKEND_DIR = ROOT_DIR / "backend"
APP_DIR = BACKEND_DIR / "app"
for path in (ROOT_DIR, BACKEND_DIR, APP_DIR):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from backend.app.db.base import Base
from backend.app.db import models
from backend.app.schemas.users import CreateUser, UserUpdate
from backend.app.services import users_services


class UserPayload:
    def __init__(
        self,
        name: Optional[str],
        email: Optional[str],
    ) -> None:
        self.name = name
        self.email = email
        self.journal_entries = []


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
    payload = CreateUser(name=name, email=email, journal_entries=[])
    return users_services.create_user(db_session, payload)


def test_create_user_rejects_missing_fields(db_session: Session) -> None:
    payload = UserPayload(name=None, email=None)

    result = users_services.create_user(db_session, payload)

    assert result[0] is False
    assert "required" in result[1]


def test_create_user_rejects_duplicate_email(db_session: Session) -> None:
    _create_user(db_session, "Jane", "jane@example.com")

    duplicate = CreateUser(name="Jane Two", email="jane@example.com", journal_entries=[])
    result = users_services.create_user(db_session, duplicate)

    assert result[0] is False
    assert "already exists" in result[1]


def test_get_user_by_email_returns_user(db_session: Session) -> None:
    user = _create_user(db_session, "Kara", "kara@example.com")

    result = users_services.get_user_by_email(db_session, "kara@example.com")

    assert result is not False
    assert result.id == user.id


def test_get_user_by_email_missing_returns_false(db_session: Session) -> None:
    result = users_services.get_user_by_email(db_session, "missing@example.com")

    assert result[0] is False
    assert "does not exist" in result[1]


def test_update_user_success_and_missing(db_session: Session) -> None:
    user = _create_user(db_session, "Liam", "liam@example.com")

    success = users_services.update_user(
        db_session, user.id, UserUpdate(name="Liam Updated", email="liam2@example.com")
    )
    missing = users_services.update_user(
        db_session, user.id + 1, UserUpdate(name="No One")
    )

    assert success[0] is True
    assert "Successfully" in success[1]
    assert missing[0] is False
    assert "does not exist" in missing[1]


def test_delete_user_success_and_missing(db_session: Session) -> None:
    user = _create_user(db_session, "Mia", "mia@example.com")

    success = users_services.delete_user(db_session, user.id)
    missing = users_services.delete_user(db_session, user.id + 1)

    assert success[0] is True
    assert "Successfully" in success[1]
    assert missing[0] is False


def test_get_all_users_returns_list(db_session: Session) -> None:
    _create_user(db_session, "Nia", "nia@example.com")
    _create_user(db_session, "Owen", "owen@example.com")

    users = users_services.get_all_users(db_session)

    assert len(users) == 2


def test_get_user_by_name_success_and_missing(db_session: Session) -> None:
    user = _create_user(db_session, "Pax", "pax@example.com")

    found = users_services.get_user_by_name(db_session, "Pax")
    missing = users_services.get_user_by_name(db_session, "Missing")

    assert found is not False
    assert found.id == user.id
    assert missing[0] is False


def test_get_user_by_journal_entry_id(db_session: Session) -> None:
    user = _create_user(db_session, "Quin", "quin@example.com")
    journal = models.Journal(
        user_id=user.id,
        date=date(2024, 8, 2),
        mood_rating=5,
        entry="Feeling great.",
    )
    db_session.add(journal)
    db_session.commit()

    result = users_services.get_user_by_journal_entry_id(db_session, journal.id)

    assert result is not False
    assert result.id == user.id


def test_user_exists_success_and_missing(db_session: Session) -> None:
    user = _create_user(db_session, "Rae", "rae@example.com")

    exists = users_services.user_exists(db_session, user.id)
    missing = users_services.user_exists(db_session, user.id + 1)

    assert exists is True
    assert missing[0] is False
