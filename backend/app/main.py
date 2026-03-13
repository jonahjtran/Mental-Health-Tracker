from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware

from backend.app.api.v1 import auth, health, insights, journals, users
from backend.app.core.config import settings
from backend.app.db.init_db import init_db

app = FastAPI()

app.add_middleware(
    SessionMiddleware,
    secret_key=settings.jwt_secret,
)

app.include_router(health.router, prefix="/api/v1")
app.include_router(auth.router, prefix="/api/v1")
app.include_router(users.router, prefix="/api/v1")
app.include_router(journals.router, prefix="/api/v1")
app.include_router(insights.router, prefix="/api/v1")


@app.on_event("startup")
def on_startup() -> None:
    init_db()
