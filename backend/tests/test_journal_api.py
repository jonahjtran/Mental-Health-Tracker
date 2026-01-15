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
    config_module.settings = types.SimpleNamespace(
        database_url="sqlite+pysqlite:///:memory:",
        jwt_secret="test-jwt-secret",
        jwt_expiration_minutes=60,
        google_client_id="test-client-id",
        google_client_secret="test-client-secret",
        google_redirect_uri="http://localhost:8000/api/v1/auth/callback/google",
        frontend_url="http://frontend.test",
    )
    sys.modules["app.core.config"] = config_module

if "backend.app.core.config" not in sys.modules:
    config_module = types.ModuleType("backend.app.core.config")
    config_module.settings = types.SimpleNamespace(
        database_url="sqlite+pysqlite:///:memory:",
        jwt_secret="test-jwt-secret",
        jwt_expiration_minutes=60,
        google_client_id="test-client-id",
        google_client_secret="test-client-secret",
        google_redirect_uri="http://localhost:8000/api/v1/auth/callback/google",
        frontend_url="http://frontend.test",
    )
    sys.modules["backend.app.core.config"] = config_module

from backend.app.api.v1 import journals as journals_router
from backend.app.db.base import Base
from backend.app.db import models
from backend.app.db.session import get_db
from backend.app.core.security import get_current_user


CURRENT_USER = {"user": None}


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
    app.dependency_overrides[get_current_user] = lambda: CURRENT_USER["user"]

    with TestClient(app) as test_client:
        CURRENT_USER["user"] = None
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
    CURRENT_USER["user"] = user
    payload = {"date": "2024-07-01", "mood_rating": 4, "entry": "Feeling good."}

    response = client.post("/me/journals", json=payload)

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

    CURRENT_USER["user"] = user
    ok = client.get(f"/me/journals/{journal.id}")
    assert ok.status_code == 200

    CURRENT_USER["user"] = other
    forbidden = client.get(f"/me/journals/{journal.id}")
    assert forbidden.status_code == 404


def test_get_journal_by_date_returns_entries(client: TestClient, db_session: Session) -> None:
    user = _create_user(db_session, "Uma", "uma@example.com")
    _create_journal(db_session, user.id, entry="Day one.", mood_rating=2)
    CURRENT_USER["user"] = user

    response = client.get("/me/journals", params={"date": "2024-07-01"})

    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    assert body[0]["entry"] == "Day one."


def test_get_journal_by_mood_rating_validates_range(client: TestClient, db_session: Session) -> None:
    user = _create_user(db_session, "Vic", "vic@example.com")
    CURRENT_USER["user"] = user

    response = client.get("/me/journals", params={"mood_rating": 0})

    assert response.status_code == 422


def test_update_journal_endpoint_updates_row(client: TestClient, db_session: Session) -> None:
    user = _create_user(db_session, "Wes", "wes@example.com")
    journal = _create_journal(db_session, user.id, entry="Before.", mood_rating=2)
    payload = {"entry": "After."}
    CURRENT_USER["user"] = user

    response = client.patch(f"/me/journals/{journal.id}", json=payload)

    assert response.status_code == 200
    body = response.json()
    assert body["entry"] == "After."
    db_session.expire_all()
    stored = db_session.get(models.Journal, journal.id)
    assert stored.entry == "After."


def test_delete_journal_endpoint_removes_row(client: TestClient, db_session: Session) -> None:
    user = _create_user(db_session, "Zoe", "zoe@example.com")
    journal = _create_journal(db_session, user.id, entry="Gone.", mood_rating=5)
    journal_id = journal.id
    CURRENT_USER["user"] = user

    response = client.delete(f"/me/journals/{journal_id}")

    assert response.status_code == 200
    db_session.expire_all()
    stored = db_session.get(models.Journal, journal_id)
    assert stored is None
