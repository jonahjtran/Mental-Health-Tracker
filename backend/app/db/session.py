from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from collections.abc import Generator
from backend.app.core.config import settings
from sqlalchemy.orm import Session

SQLALCHEMY_DATABASE_URL = settings.database_url  # from backend.app.core.config
engine = create_engine(SQLALCHEMY_DATABASE_URL, future=True, echo=False, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
