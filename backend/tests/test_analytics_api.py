import sys
import types
from datetime import date, timedelta
from pathlib import Path

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
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
        insights_model="test-model",
        insights_api_key="test-key",
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
        insights_model="test-model",
        insights_api_key="test-key",
    )
    sys.modules["backend.app.core.config"] = config_module

from backend.app.api.v1 import analytics as analytics_router
from backend.app.core.security import get_current_user
from backend.app.db import models
from backend.app.db.base import Base
from backend.app.db.session import get_db


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
    app.include_router(analytics_router.router, prefix="/api/v1")

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


def _create_journal(db_session: Session, user_id: int, *, entry_date: date, mood_rating: int) -> models.Journal:
    journal = models.Journal(user_id=user_id, date=entry_date, mood_rating=mood_rating, entry="Entry.")
    db_session.add(journal)
    db_session.commit()
    db_session.refresh(journal)
    return journal


def _flag_journal(db_session: Session, journal: models.Journal, *, risk_flag: bool, risk_reason=None) -> None:
    insights = models.JournalInsights(
        journal_id=journal.id,
        user_id=journal.user_id,
        summary="Summary.",
        themes=[],
        sentiment={"label": "neutral", "score": 0.5},
        suggestions=[],
        risk_flag=risk_flag,
        risk_reason=risk_reason,
        model_name="test-model",
    )
    db_session.add(insights)
    db_session.commit()


def test_analytics_computes_stats_for_range(client: TestClient, db_session: Session) -> None:
    user = _create_user(db_session, "Ada", "ada@example.com")
    today = date.today()
    j1 = _create_journal(db_session, user.id, entry_date=today, mood_rating=4)
    j2 = _create_journal(db_session, user.id, entry_date=today - timedelta(days=1), mood_rating=2)
    _flag_journal(db_session, j1, risk_flag=False)
    _flag_journal(db_session, j2, risk_flag=True, risk_reason="Mentioned hopelessness.")
    CURRENT_USER["user"] = user

    response = client.get("/api/v1/me/analytics")

    assert response.status_code == 200
    body = response.json()
    assert body["entry_count"] == 2
    assert body["average_mood"] == 3.0
    assert body["mood_distribution"] == {"4": 1, "2": 1}
    assert body["current_streak_days"] == 2
    assert body["risk_flag_count"] == 1


def test_analytics_empty_range_returns_zeroed_fields(client: TestClient, db_session: Session) -> None:
    user = _create_user(db_session, "Ben", "ben@example.com")
    CURRENT_USER["user"] = user

    response = client.get("/api/v1/me/analytics")

    assert response.status_code == 200
    body = response.json()
    assert body["entry_count"] == 0
    assert body["average_mood"] is None
    assert body["mood_by_date"] == []
    assert body["mood_distribution"] == {}
    assert body["current_streak_days"] == 0
    assert body["risk_flag_count"] == 0


def test_analytics_respects_custom_date_range(client: TestClient, db_session: Session) -> None:
    user = _create_user(db_session, "Cy", "cy@example.com")
    today = date.today()
    _create_journal(db_session, user.id, entry_date=today - timedelta(days=10), mood_rating=5)
    _create_journal(db_session, user.id, entry_date=today, mood_rating=1)
    CURRENT_USER["user"] = user

    response = client.get(
        "/api/v1/me/analytics",
        params={"start_date": str(today), "end_date": str(today)},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["entry_count"] == 1
    assert body["average_mood"] == 1.0
