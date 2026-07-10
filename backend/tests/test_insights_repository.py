import sys
from pathlib import Path
from datetime import date

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker


ROOT_DIR = Path(__file__).resolve().parents[2]
BACKEND_DIR = ROOT_DIR / "backend"
APP_DIR = BACKEND_DIR / "app"
for path in (ROOT_DIR, BACKEND_DIR, APP_DIR):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from backend.app.db.base import Base
from backend.app.db import models
from backend.app.repositories.insights_repository import get_flagged_insights


@pytest.fixture()
def db_session() -> Session:
    engine = create_engine("sqlite+pysqlite:///:memory:", future=True)
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
    session = SessionLocal()

    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


def _create_user(db_session: Session, name: str, email: str) -> models.Users:
    user = models.Users(name=name, email=email)
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


def _create_journal(db_session: Session, user_id: int, entry: str) -> models.Journal:
    journal = models.Journal(user_id=user_id, date=date(2024, 5, 1), mood_rating=2, entry=entry)
    db_session.add(journal)
    db_session.commit()
    db_session.refresh(journal)
    return journal


def _create_insights(db_session: Session, journal: models.Journal, *, risk_flag: bool) -> models.JournalInsights:
    insights = models.JournalInsights(
        journal_id=journal.id,
        user_id=journal.user_id,
        summary="Summary.",
        themes=[],
        sentiment={"label": "neutral", "score": 0.5},
        suggestions=[],
        risk_flag=risk_flag,
        risk_reason="Reason." if risk_flag else None,
        model_name="test-model",
    )
    db_session.add(insights)
    db_session.commit()
    db_session.refresh(insights)
    return insights


def test_get_flagged_insights_returns_only_flagged_for_user(db_session: Session) -> None:
    user = _create_user(db_session, "Kai", "kai@example.com")
    other_user = _create_user(db_session, "Lou", "lou@example.com")

    flagged_journal = _create_journal(db_session, user.id, "Struggling.")
    calm_journal = _create_journal(db_session, user.id, "Fine.")
    other_flagged_journal = _create_journal(db_session, other_user.id, "Also struggling.")

    _create_insights(db_session, flagged_journal, risk_flag=True)
    _create_insights(db_session, calm_journal, risk_flag=False)
    _create_insights(db_session, other_flagged_journal, risk_flag=True)

    result = get_flagged_insights(db_session, user.id)

    assert len(result) == 1
    assert result[0].journal_id == flagged_journal.id
