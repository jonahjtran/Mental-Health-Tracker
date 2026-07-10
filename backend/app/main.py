from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

from backend.app.api.v1 import analytics, auth, health, insights, journals, users
from backend.app.core.config import settings
from backend.app.db.init_db import init_db

app = FastAPI()

app.add_middleware(
    SessionMiddleware,
    secret_key=settings.jwt_secret,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix="/api/v1")
app.include_router(auth.router, prefix="/api/v1")
app.include_router(users.router, prefix="/api/v1")
app.include_router(journals.router, prefix="/api/v1")
app.include_router(insights.router, prefix="/api/v1")
app.include_router(analytics.router, prefix="/api/v1")


@app.on_event("startup")
def on_startup() -> None:
    init_db()
