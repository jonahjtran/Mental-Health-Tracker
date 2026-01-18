from backend.app.db.models import JournalInsights
from sqlalchemy.orm import Session
from backend.app.schemas.journal import JournalAnalysisOut, JournalAnalysisUpdate
from backend.app.core.config import settings
from datetime import datetime
from backend.app.services.errors import NotFoundError

def get_existing_insights_repository(db: Session, journal_id: int, user_id: int):
    return db.query(JournalInsights).filter(JournalInsights.journal_id == journal_id, JournalInsights.user_id == user_id).first()

def save_insights(db: Session, journal_id: int, user_id: int, insights: JournalAnalysisOut):
    new_insights = JournalInsights(
        journal_id=journal_id,
        user_id=user_id,
        summary=insights.summary,
        themes=insights.themes,
        sentiment=insights.sentiment,
        suggestions=insights.suggestions,
        risk_flag=insights.risk_flag,
        risk_reason=insights.risk_reason,
        model_name=settings.insights_model,

    )
    db.add(new_insights)
    db.commit()
    db.refresh(new_insights)
    return new_insights

def delete_insights_repository(db: Session, journal_id: int, user_id: int):
    db.query(JournalInsights).filter(JournalInsights.journal_id == journal_id, JournalInsights.user_id == user_id).delete()
    db.commit()
    return True

def update_insights_repository(db: Session, journal_id: int, user_id: int, insights: JournalAnalysisUpdate):
    existing_insights = insights.model_dump(exclude_unset=True)
    if existing_insights:
        db.query(JournalInsights).filter(JournalInsights.journal_id == journal_id, JournalInsights.user_id == user_id)
    db.commit()
    return True
    