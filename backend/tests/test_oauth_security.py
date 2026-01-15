import os
import sys
from pathlib import Path

import jwt


os.environ.setdefault("DATABASE_URL", "sqlite+pysqlite:///:memory:")
os.environ.setdefault("JWT_SECRET", "test-jwt-secret")
os.environ.setdefault("JWT_EXPIRES_MINUTES", "60")
os.environ.setdefault("GOOGLE_CLIENT_ID", "test-client-id")
os.environ.setdefault("GOOGLE_CLIENT_SECRET", "test-client-secret")
os.environ.setdefault(
    "GOOGLE_REDIRECT_URI", "http://localhost:8000/api/v1/auth/callback/google"
)
os.environ.setdefault("FRONTEND_URL", "http://localhost:3000")


ROOT_DIR = Path(__file__).resolve().parents[2]
BACKEND_DIR = ROOT_DIR / "backend"
APP_DIR = BACKEND_DIR / "app"
for path in (ROOT_DIR, BACKEND_DIR, APP_DIR):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from backend.app.core.config import settings
from backend.app.core import security


def test_create_access_token_encodes_subject() -> None:
    token = security.create_access_token(user_id=42)

    payload = jwt.decode(token, settings.jwt_secret, algorithms=["HS256"])

    assert payload["sub"] == "42"
    assert "exp" in payload
