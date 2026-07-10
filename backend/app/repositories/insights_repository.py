from backend.app.db.models import JournalInsights
from sqlalchemy.orm import Session
from backend.app.schemas.journal import JournalAnalysisOut, JournalAnalysisUpdate
from backend.app.core.config import settings
from typing import Optional, Union

def get_existing_insights_repository(db: Session, journal_id: int, user_id: int):
    return db.query(JournalInsights).filter(JournalInsights.journal_id == journal_id, JournalInsights.user_id == user_id).first()

def get_flagged_insights(db: Session, user_id: int):
    return (
        db.query(JournalInsights)
        .filter(JournalInsights.user_id == user_id, JournalInsights.risk_flag == True)  # noqa: E712
        .order_by(JournalInsights.created_at.desc())
        .all()
    )

def save_insights(db: Session, journal_id: int, user_id: int, insights: JournalAnalysisOut):
    new_insights = JournalInsights(
        journal_id=journal_id,
        user_id=user_id,
        summary=insights.summary,
        themes=insights.themes,
        sentiment=insights.sentiment.model_dump(),
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

def update_insights_repository(
    db: Session,
    journal_id: int,
    user_id: int,
    insights: Union[JournalAnalysisUpdate, JournalAnalysisOut],
    *,
    model_name: Optional[str] = None,
):
    update_data = insights.model_dump(exclude_unset=True)
    if model_name is not None:
        update_data["model_name"] = model_name
    if update_data:
        db.query(JournalInsights).filter(
            JournalInsights.journal_id == journal_id,
            JournalInsights.user_id == user_id,
        ).update(update_data)
    db.commit()
    return get_existing_insights_repository(db, journal_id, user_id)
