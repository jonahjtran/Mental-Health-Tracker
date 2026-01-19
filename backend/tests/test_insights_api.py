import json
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

GENAI_RESPONSE_TEXT = json.dumps(
    {
        "summary": "Refreshed summary.",
        "themes": ["growth"],
        "sentiment": {"label": "positive", "score": 0.88},
        "suggestions": ["Keep journaling."],
        "risk_flag": False,
        "risk_reason": None,
    }
)

google_module = types.ModuleType("google")
genai_module = types.ModuleType("google.genai")


class DummyModels:
    def generate_content(self, model, contents):
        return types.SimpleNamespace(text=GENAI_RESPONSE_TEXT)


class DummyClient:
    def __init__(self, api_key):
        self.models = DummyModels()


genai_module.Client = DummyClient
google_module.genai = genai_module
sys.modules["google"] = google_module
sys.modules["google.genai"] = genai_module

from backend.app.api.v1 import insights as insights_router
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
    app.include_router(insights_router.router)

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


def _create_insights(db_session: Session, journal_id: int, user_id: int):
    insights = models.JournalInsights(
        journal_id=journal_id,
        user_id=user_id,
        summary="Initial summary.",
        themes=["routine"],
        sentiment={"label": "neutral", "score": 0.5},
        suggestions=["Rest."],
        risk_flag=False,
        risk_reason=None,
        model_name="seed-model",
    )
    db_session.add(insights)
    db_session.commit()
    db_session.refresh(insights)
    return insights


def test_get_insights_endpoint_returns_data(client: TestClient, db_session: Session) -> None:
    user = _create_user(db_session, "Nia", "nia@example.com")
    journal = _create_journal(db_session, user.id, entry="Entry.", mood_rating=3)
    _create_insights(db_session, journal.id, user.id)
    CURRENT_USER["user"] = user

    response = client.get(f"/api/v1/insights/me/journals/{journal.id}/insights")

    assert response.status_code == 200
    body = response.json()
    assert body["summary"] == "Initial summary."
    assert body["sentiment"]["label"] == "neutral"


def test_update_insights_endpoint_reanalyzes(client: TestClient, db_session: Session) -> None:
    user = _create_user(db_session, "Omar", "omar@example.com")
    journal = _create_journal(db_session, user.id, entry="Entry.", mood_rating=4)
    _create_insights(db_session, journal.id, user.id)
    CURRENT_USER["user"] = user

    response = client.put(
        f"/api/v1/insights/me/journals/{journal.id}/insights",
        json={},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["summary"] == "Refreshed summary."
    db_session.expire_all()
    stored = db_session.execute(
        select(models.JournalInsights).where(models.JournalInsights.journal_id == journal.id)
    ).scalar_one()
    assert stored.summary == "Refreshed summary."
    assert stored.model_name == "test-model"


def test_delete_insights_endpoint_deletes(client: TestClient, db_session: Session) -> None:
    user = _create_user(db_session, "Pia", "pia@example.com")
    journal = _create_journal(db_session, user.id, entry="Entry.", mood_rating=2)
    _create_insights(db_session, journal.id, user.id)
    CURRENT_USER["user"] = user

    response = client.delete(f"/api/v1/insights/me/journals/{journal.id}/insights")

    assert response.status_code == 204
    db_session.expire_all()
    stored = db_session.execute(
        select(models.JournalInsights).where(models.JournalInsights.journal_id == journal.id)
    ).scalar_one_or_none()
    assert stored is None
