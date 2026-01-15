from sqlalchemy import null
from app.db import models
from pydantic import BaseModel
from typing import List, Optional
from app.schemas.journal import JournalRead


class CreateUser(BaseModel):
    name: str
    email: str
    journal_entries: List[JournalRead]

    class Config:
        from_attributes = True

class UserRead(BaseModel):
    id: int
    name: str
    email: str
    journal_entries: List[JournalRead]

    class Config:
        from_attributes = True

class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    journal_entries: Optional[List[JournalRead]] = None

    class Config:
        from_attributes = True

class UserDelete(BaseModel):
    id: int

    class Config:
        from_attributes = True

class GetUserByEmail(BaseModel):
    email: str

    class Config:
        from_attributes = True

class GetUserById(BaseModel):
    id: int

    class Config:
        from_attributes = True
