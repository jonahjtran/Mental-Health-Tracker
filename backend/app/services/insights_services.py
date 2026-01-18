from backend.app import db
from backend.app.db.models import JournalInsights
from backend.app.repositories.insights_repository import get_existing_insights_repository
from backend.app.repositories.journal_repository import get_journal_entry
from backend.app.core.config import settings
from backend.app.ai.prompt import INSIGHTS_PROMPT
from backend.app.schemas.journal import JournalAnalysisOut
from backend.app.repositories.insights_repository import save_insights, delete_insights_repository, update_insights_repository
from backend.app.services.errors import NotFoundError
from backend.app.schemas.journal import JournalAnalysisUpdate
from google import genai
from sqlalchemy.orm import Session
import json
from pydantic import ValidationError


"@TODO: return a JournalAnalysisOut object if it already exists, not jsut when creating new one"
def analyze_journal_entry(db: Session,journal_id: int, user_id: int, force=False):
    existing_insights = get_existing_insights_repository(db, journal_id, user_id)

    journal_entry = get_journal_entry(db, journal_id, user_id)
    if not journal_entry:
        raise ValueError(f"Journal entry does not exist for user {user_id}")
    
    if existing_insights and not force:
        return existing_insights
     
    mood_rating = journal_entry.mood_rating
    entry = journal_entry.entry
    date = journal_entry.date

    client = genai.Client(api_key=settings.insights_api_key)

    prompt = INSIGHTS_PROMPT.format(date=date, mood_rating=mood_rating, entry=entry)

    response = client.models.generate_content(model=settings.insights_model, contents=prompt)

    insights = parse_insights(response.text)

    save_insights(db, journal_id, user_id, insights)

    return insights

def parse_insights(response_text: str) -> JournalAnalysisOut:
    try:
        data = json.loads(response_text)
        return JournalAnalysisOut.model_validate(data)
    except (json.JSONDecodeError, ValidationError) as exc:
        raise ValueError("Invalid analysis output") from exc


def delete_insights(db: Session, journal_id: int, user_id: int):
    existing_insights = get_existing_insights_repository(db, journal_id, user_id)
    if not existing_insights:
        raise NotFoundError("Insights not found")
    delete_insights_repository(db, journal_id, user_id)
    return existing_insights

def update_insights(db: Session, journal_id: int, user_id: int, insights: JournalAnalysisUpdate, force: bool = True):
    existing_insights = get_existing_insights_repository(db, journal_id, user_id)
    if not existing_insights:
        raise NotFoundError("Existing insights not found")
    update_insights_repository(db, journal_id, user_id, insights)
    
    updated_insights = get_existing_insights_repository(db, journal_id, user_id)
    return updated_insights

def get_insights(db: Session, journal_id: int, user_id: int):
    existing_insights = get_existing_insights_repository(db, journal_id, user_id)
    if not existing_insights:
        raise NotFoundError("Existing insights not found")
    return existing_insights