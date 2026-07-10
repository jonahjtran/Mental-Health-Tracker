from collections import Counter
from datetime import date, timedelta

from sqlalchemy.orm import Session

from backend.app.db.models import JournalInsights
from backend.app.repositories.journal_repository import (
    get_journals_by_user,
    get_journals_in_range,
)
from backend.app.repositories.user_repository import user_exists
from backend.app.schemas.analytics import AnalyticsOut, MoodPoint
from backend.app.services.errors import NotFoundError

DEFAULT_RANGE_DAYS = 30


def get_analytics(db: Session, user_id: int, *, start_date: date = None, end_date: date = None) -> AnalyticsOut:
    if user_exists(db, user_id) is False:
        raise NotFoundError("User not found.")

    if end_date is None:
        end_date = date.today()
    if start_date is None:
        start_date = end_date - timedelta(days=DEFAULT_RANGE_DAYS - 1)

    journals = get_journals_in_range(db, user_id, start_date, end_date)

    entry_count = len(journals)
    average_mood = round(sum(j.mood_rating for j in journals) / entry_count, 2) if entry_count else None
    mood_by_date = [MoodPoint(date=j.date, mood_rating=j.mood_rating) for j in journals]
    mood_distribution = dict(Counter(j.mood_rating for j in journals))

    journal_ids = [j.id for j in journals]
    risk_flag_count = (
        db.query(JournalInsights)
        .filter(JournalInsights.journal_id.in_(journal_ids), JournalInsights.risk_flag == True)  # noqa: E712
        .count()
        if journal_ids
        else 0
    )

    current_streak_days = _compute_current_streak(db, user_id)

    return AnalyticsOut(
        average_mood=average_mood,
        mood_by_date=mood_by_date,
        mood_distribution=mood_distribution,
        entry_count=entry_count,
        current_streak_days=current_streak_days,
        risk_flag_count=risk_flag_count,
    )


def _compute_current_streak(db: Session, user_id: int) -> int:
    all_journals = get_journals_by_user(db, user_id)
    entry_dates = {j.date for j in all_journals}

    streak = 0
    cursor = date.today()
    while cursor in entry_dates:
        streak += 1
        cursor -= timedelta(days=1)
    return streak
