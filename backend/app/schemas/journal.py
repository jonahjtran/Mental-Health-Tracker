from backend.app.db import models
from pydantic import BaseModel
from datetime import date


class JournalCreate(BaseModel):
    user_id: int
    date: date
    mood_rating: int
    entry: str

class JournalRead(BaseModel):
    id: int
    date: date
    mood_rating: int
    entry: str

    class Config:
        from_attributes = True