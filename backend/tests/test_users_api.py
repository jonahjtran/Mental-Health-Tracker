import sys
import types
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

from backend.app.api.v1 import users as users_router
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
    app.include_router(users_router.router, prefix="/api/v1")

    def _get_db():
        db = db_sessionmaker()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = _get_db

    with TestClient(app) as test_client:
        yield test_client


def test_create_user_endpoint_creates_user_without_journal_entries(
    client: TestClient, db_session: Session
) -> None:
    response = client.post(
        "/api/v1/users",
        json={"name": "Jonah Tran", "email": "jonahjtran@gmail.com"},
    )

    assert response.status_code == 201
    body = response.json()
    assert body["name"] == "Jonah Tran"
    assert body["email"] == "jonahjtran@gmail.com"
    assert body["journal_entries"] == []

    stored = db_session.query(models.Users).filter_by(email="jonahjtran@gmail.com").first()
    assert stored is not None
