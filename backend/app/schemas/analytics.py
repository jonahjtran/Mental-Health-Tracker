from datetime import date as dt_date
from typing import Dict, List, Optional

from pydantic import BaseModel


class MoodPoint(BaseModel):
    date: dt_date
    mood_rating: int


class AnalyticsOut(BaseModel):
    average_mood: Optional[float]
    mood_by_date: List[MoodPoint]
    mood_distribution: Dict[int, int]
    entry_count: int
    current_streak_days: int
    risk_flag_count: int


class RiskFlagOut(BaseModel):
    journal_id: int
    date: dt_date
    risk_reason: Optional[str]
