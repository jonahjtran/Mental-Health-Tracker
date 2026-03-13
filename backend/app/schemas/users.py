from pydantic import BaseModel, ConfigDict, Field
from typing import List, Optional
from backend.app.schemas.journal import JournalRead


class CreateUser(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str
    email: str

class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: str
    journal_entries: List[JournalRead] = Field(default_factory=list)

class UserUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: Optional[str] = None
    email: Optional[str] = None

class UserDelete(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int

class GetUserByEmail(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    email: str

class GetUserById(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
