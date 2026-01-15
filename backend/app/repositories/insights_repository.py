from backend.app.db.models import JournalInsights
from sqlalchemy.orm import Session

def get_existing_insights(db: Session, journal_id: int, user_id: int):
    return db.query(JournalInsights).filter(JournalInsights.journal_id == journal_id, JournalInsights.user_id == user_id).first()