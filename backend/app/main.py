from fastapi import FastAPI
from backend.app.api.v1 import auth

from starlette.middleware.sessions import SessionMiddleware
from backend.app.core.config import settings

app = FastAPI()

app.include_router(auth.router, prefix="/api/v1")


app.add_middleware(
    SessionMiddleware,
    secret_key=settings.jwt_secret,
)


