import sys
import types
from datetime import date
from pathlib import Path

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool


ROOT_DIR = Path(__file__).resolve().parents[2]
BACKEND_DIR = ROOT_DIR / "backend"
APP_DIR = BACKEND_DIR / "app"
for path in (ROOT_DIR, BACKEND_DIR, APP_DIR):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

if "app.core.config" not in sys.modules:
    config_module = types.ModuleType("app.core.config")
    config_module.settings = types.SimpleNamespace(database_url="sqlite+pysqlite:///:memory:")
    sys.modules["app.core.config"] = config_module

from backend.app.api.v1 import journals as journals_router
from backend.app.db.base import Base
from backend.app.db import models
from backend.app.db.session import get_db


@pytest.fixture()
def db_engine():
    engine = create_engine(
        "sqlite+pysqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        future=True,
    )
    Base.metadata.create_all(bind=engine)
    try:
        yield engine
    finally:
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


@pytest.fixture()
def db_sessionmaker(db_engine):
    return sessionmaker(bind=db_engine, autocommit=False, autoflush=False)


@pytest.fixture()
def db_session(db_sessionmaker) -> Session:
    session = db_sessionmaker()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture()
def client(db_sessionmaker):
    app = FastAPI()
    app.include_router(journals_router.router)

    def _get_db():
        db = db_sessionmaker()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = _get_db

    with TestClient(app) as test_client:
        yield test_client


def _create_user(db_session: Session, name: str, email: str) -> models.Users:
    user = models.Users(name=name, email=email)
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


def _create_journal(db_session: Session, user_id: int, *, entry: str, mood_rating: int):
    journal = models.Journal(
        user_id=user_id,
        date=date(2024, 7, 1),
        mood_rating=mood_rating,
        entry=entry,
    )
    db_session.add(journal)
    db_session.commit()
    db_session.refresh(journal)
    return journal


def test_create_journal_endpoint_persists(client: TestClient, db_session: Session) -> None:
    user = _create_user(db_session, "Rita", "rita@example.com")
    payload = {"date": "2024-07-01", "mood_rating": 4, "entry": "Feeling good."}

    response = client.post(f"/journals/create/{user.id}", json=payload)

    assert response.status_code == 201
    body = response.json()
    assert body["entry"] == "Feeling good."
    assert body["mood_rating"] == 4
    stored = db_session.execute(select(models.Journal)).scalars().all()
    assert len(stored) == 1


def test_get_journal_by_id_requires_matching_user(client: TestClient, db_session: Session) -> None:
    user = _create_user(db_session, "Sam", "sam@example.com")
    other = _create_user(db_session, "Tia", "tia@example.com")
    journal = _create_journal(db_session, user.id, entry="Scoped.", mood_rating=3)

    ok = client.get(f"/journals/id/{journal.id}", params={"user_id": user.id})
    assert ok.status_code == 200

    forbidden = client.get(f"/journals/id/{journal.id}", params={"user_id": other.id})
    assert forbidden.status_code == 404


def test_get_journal_by_date_returns_entries(client: TestClient, db_session: Session) -> None:
    user = _create_user(db_session, "Uma", "uma@example.com")
    _create_journal(db_session, user.id, entry="Day one.", mood_rating=2)

    response = client.get("/journals/date/2024-07-01", params={"user_id": user.id})

    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    assert body[0]["entry"] == "Day one."


def test_get_journal_by_mood_rating_validates_range(client: TestClient, db_session: Session) -> None:
    user = _create_user(db_session, "Vic", "vic@example.com")

    response = client.get("/journals/mood/0", params={"user_id": user.id})

    assert response.status_code == 422


def test_update_journal_endpoint_updates_row(client: TestClient, db_session: Session) -> None:
    user = _create_user(db_session, "Wes", "wes@example.com")
    journal = _create_journal(db_session, user.id, entry="Before.", mood_rating=2)
    payload = {"entry": "After."}

    response = client.put(f"/journals/update/{journal.id}", json=payload)

    assert response.status_code == 200
    body = response.json()
    assert body["entry"] == "After."
    db_session.expire_all()
    stored = db_session.get(models.Journal, journal.id)
    assert stored.entry == "After."


def test_delete_journal_endpoint_removes_row(client: TestClient, db_session: Session) -> None:
    user = _create_user(db_session, "Zoe", "zoe@example.com")
    journal = _create_journal(db_session, user.id, entry="Gone.", mood_rating=5)

    response = client.delete(f"/journals/delete/{journal.id}")

    assert response.status_code == 200
    db_session.expire_all()
    stored = db_session.get(models.Journal, journal.id)
    assert stored is None
