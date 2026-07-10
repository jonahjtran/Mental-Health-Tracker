from pydantic import BaseModel, ConfigDict
from datetime import date as dt_date
from pydantic import Field
from typing import Optional, List

class JournalCreate(BaseModel):
    date: Optional[dt_date] = Field(default_factory=dt_date.today)
    mood_rating: int = Field(..., ge=1, le=5)
    entry: str

class JournalRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    date: dt_date
    mood_rating: int = Field(..., ge=1, le=5)
    entry: str

class JournalUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    date: Optional[dt_date] = None
    mood_rating: Optional[int] = Field(None, ge=1, le=5)
    entry: Optional[str] = None

class Sentiment(BaseModel):
    model_config = ConfigDict(extra="forbid")

    label: str
    score: float = Field(..., ge=0, le=1)

class JournalAnalysisOut(BaseModel):
    model_config = ConfigDict(from_attributes=True, extra="forbid")

    summary: str
    themes: List[str]
    sentiment: Sentiment
    suggestions: List[str]
    risk_flag: bool
    risk_reason: Optional[str]

class JournalAnalysisUpdate(BaseModel):
    summary: Optional[str] = None
    themes: Optional[List[str]] = None
    sentiment: Optional[Sentiment] = None
    suggestions: Optional[List[str]] = None
    risk_flag: Optional[bool] = None
    risk_reason: Optional[str] = None

