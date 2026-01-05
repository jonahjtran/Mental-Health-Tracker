from pydantic import BaseModel
from datetime import date
from pydantic import Field
from typing import Optional

class JournalCreate(BaseModel):
        date: date = Field(default=date.today())
        mood_rating: int = 
        entry: str

class JournalRead(BaseModel):
    id: int
    date: date
    mood_rating: int = Field(..., ge=1, le=5)
    entry: str

    class Config:
        from_attributes = True

class JournalUpdate(BaseModel):
    date: Optional[date] = None
    mood_rating: Optional[int] = Field(..., ge=1, le=5)
    entry: Optional[str] = None

    class Config:
        from_attributes = True