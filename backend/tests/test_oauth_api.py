import os
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool
from starlette.middleware.sessions import SessionMiddleware
from starlette.responses import RedirectResponse


os.environ.setdefault("DATABASE_URL", "sqlite+pysqlite:///:memory:")
os.environ.setdefault("JWT_SECRET", "test-jwt-secret")
os.environ.setdefault("JWT_EXPIRES_MINUTES", "60")
os.environ.setdefault("GOOGLE_CLIENT_ID", "test-client-id")
os.environ.setdefault("GOOGLE_CLIENT_SECRET", "test-client-secret")
os.environ.setdefault(
    "GOOGLE_REDIRECT_URI", "http://localhost:8000/api/v1/auth/callback/google"
)
os.environ.setdefault("FRONTEND_URL", "http://frontend.test")


ROOT_DIR = Path(__file__).resolve().parents[2]
BACKEND_DIR = ROOT_DIR / "backend"
APP_DIR = BACKEND_DIR / "app"
for path in (ROOT_DIR, BACKEND_DIR, APP_DIR):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from backend.app.api.v1 import auth as auth_router
from backend.app.core.config import settings
from backend.app.db.base import Base
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
def client(db_sessionmaker, monkeypatch):
    app = FastAPI()
    app.add_middleware(SessionMiddleware, secret_key="test-session-secret")
    app.include_router(auth_router.router, prefix="/api/v1")

    def _get_db():
        db = db_sessionmaker()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = _get_db

    setattr(settings, "frontend_url", settings.frontend_url)

    async def fake_authorize_redirect(request, redirect_uri):
        return RedirectResponse(url="https://accounts.google.com/o/oauth2/v2/auth")

    monkeypatch.setattr(
        auth_router.oauth.google, "authorize_redirect", fake_authorize_redirect
    )

    with TestClient(app) as test_client:
        yield test_client


def test_login_google_redirects(client: TestClient) -> None:
    response = client.get("/api/v1/auth/login/google", follow_redirects=False)

    assert response.status_code in {302, 307}
    assert response.headers["location"].startswith(
        "https://accounts.google.com/o/oauth2/v2/auth"
    )


def test_google_callback_sets_cookie_and_redirects(
    client: TestClient, monkeypatch
) -> None:
    async def fake_authorize_access_token(request):
        return {"access_token": "google-token"}

    async def fake_parse_id_token(request, token):
        return {
            "email": "gwen@example.com",
            "sub": "sub-999",
            "name": "Gwen",
            "picture": "http://avatar.test/4",
        }

    def fake_get_or_create_user_from_oauth(*args, **kwargs):
        return SimpleNamespace(id=123)

    def fake_create_access_token(*, user_id: int):
        return "app-token"

    monkeypatch.setattr(
        auth_router.oauth.google, "authorize_access_token", fake_authorize_access_token
    )
    monkeypatch.setattr(
        auth_router.oauth.google, "parse_id_token", fake_parse_id_token
    )
    monkeypatch.setattr(
        auth_router, "get_or_create_user_from_oauth", fake_get_or_create_user_from_oauth
    )
    monkeypatch.setattr(auth_router, "create_access_token", fake_create_access_token)

    response = client.get("/api/v1/auth/callback/google", follow_redirects=False)

    assert response.status_code in {302, 307}
    assert response.headers["location"] == settings.frontend_url
    assert "access_token=app-token" in response.headers.get("set-cookie", "")
