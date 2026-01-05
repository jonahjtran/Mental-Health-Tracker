from pydantic import BaseModel
from datetime import date as dt_date
from pydantic import Field
from typing import Optional

class JournalCreate(BaseModel):
    date: Optional[dt_date] = Field(default_factory=dt_date.today)
    mood_rating: Optional[int] = Field(..., ge=1, le=5)
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
    mood_rating: Optional[int] = Field(..., ge=1, le=5)
    entry: Optional[str] = None

    class Config:
        from_attributes = True
