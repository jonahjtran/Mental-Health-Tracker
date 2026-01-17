from pydantic import BaseModel
from datetime import date as dt_date
from pydantic import Field
from typing import Optional, List

class JournalCreate(BaseModel):
    date: Optional[dt_date] = Field(default_factory=dt_date.today)
    mood_rating: int = Field(..., ge=1, le=5)
    entry: str

class JournalRead(BaseModel):
    id: int
    date: dt_date
    mood_rating: int = Field(..., ge=1, le=5)
    entry: str

    class Config:
        from_attributes = True

class JournalUpdate(BaseModel):
    date: Optional[dt_date] = None
    mood_rating: Optional[int] = Field(None, ge=1, le=5)
    entry: Optional[str] = None

    class Config:
        from_attributes = True

class Sentiment(BaseModel):
    label: str
    score: float = Field(..., ge=0, le=1)

    class Config:
        extra = "forbid"

class JournalAnalysisOut(BaseModel):
    summary: str
    themes: List[str]
    sentiment: Sentiment
    suggestions: List[str]
    risk_flag: bool
    risk_reason: Optional[str]

    class Config:
        extra = "forbid"

class JournalAnalysisUpdate(BaseModel):
    summary: Optional[str] = None
    themes: Optional[List[str]] = None
    sentiment: Optional[Sentiment] = None
    suggestions: Optional[List[str]] = None
    risk_flag: Optional[bool] = None
    risk_reason: Optional[str] = None
