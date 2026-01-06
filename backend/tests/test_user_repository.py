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
from backend.app.repositories import user_repository
from backend.app.schemas.users import CreateUser, UserUpdate


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
    return user_repository.create_user(db_session, payload)


def test_create_user_persists(db_session: Session) -> None:
    user = _create_user(db_session, "Avery", "avery@example.com")

    assert user.id is not None
    stored = db_session.execute(select(models.Users)).scalars().all()
    assert len(stored) == 1
    assert stored[0].email == "avery@example.com"


def test_get_user_by_email_and_id(db_session: Session) -> None:
    user = _create_user(db_session, "Brett", "brett@example.com")

    by_email = user_repository.get_user_by_email(db_session, "brett@example.com")
    by_id = user_repository.get_user_by_id(db_session, user.id)

    assert by_email is not None
    assert by_email.id == user.id
    assert by_id is not None
    assert by_id.email == "brett@example.com"


def test_get_user_by_name(db_session: Session) -> None:
    _create_user(db_session, "Casey", "casey@example.com")

    found = user_repository.get_user_by_name(db_session, "Casey")

    assert found is not None
    assert found.email == "casey@example.com"


def test_update_user_persists_changes(db_session: Session) -> None:
    user = _create_user(db_session, "Devon", "devon@example.com")
    payload = UserUpdate(name="Devon Updated", email="devon2@example.com")
    print("before calling update_user")
    result = user_repository.update_user(db_session, user.id, payload)
    print("called update user function")
    assert result is True
    refreshed = user_repository.get_user_by_id(db_session, user.id)
    assert refreshed is not None
    assert refreshed.name == "Devon Updated"
    assert refreshed.email == "devon2@example.com"


def test_get_all_users_returns_everyone(db_session: Session) -> None:
    _create_user(db_session, "Eli", "eli@example.com")
    _create_user(db_session, "Fae", "fae@example.com")

    users = user_repository.get_all_users(db_session)

    assert len(users) == 2
    assert {user.email for user in users} == {"eli@example.com", "fae@example.com"}


def test_delete_user_removes_row(db_session: Session) -> None:
    user = _create_user(db_session, "Gale", "gale@example.com")

    result = user_repository.delete_user(db_session, user.id)

    assert result is True
    assert user_repository.get_user_by_id(db_session, user.id) is None


def test_get_user_by_journal_entry_id(db_session: Session) -> None:
    user = _create_user(db_session, "Hale", "hale@example.com")
    journal = models.Journal(
        user_id=user.id,
        date=date(2024, 8, 1),
        mood_rating=4,
        entry="Solid day.",
    )
    db_session.add(journal)
    db_session.commit()

    found = user_repository.get_user_by_journal_entry_id(db_session, journal.id)

    assert found is not None
    assert found.id == user.id
    assert found.email == "hale@example.com"


def test_user_exists_true_and_false(db_session: Session) -> None:
    user = _create_user(db_session, "Ira", "ira@example.com")

    assert user_repository.user_exists(db_session, user.id) is True
    assert user_repository.user_exists(db_session, user.id + 1) is False
