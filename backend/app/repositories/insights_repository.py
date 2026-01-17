from backend.app.db.models import JournalInsights
from sqlalchemy.orm import Session
from backend.app.schemas.journal import JournalAnalysisOut
from backend.app.core.config import settings
from datetime import datetime

def get_existing_insights(db: Session, journal_id: int, user_id: int):
    return db.query(JournalInsights).filter(JournalInsights.journal_id == journal_id, JournalInsights.user_id == user_id).first()

def save_insights(db: Session, journal_id: int, user_id: int, insights: JournalAnalysisOut):
    insights = JournalInsights(
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
    db.add(insights)
    db.commit()
    db.refresh(insights)
    return insights