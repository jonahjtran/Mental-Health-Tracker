from sqlalchemy import null
from backend.app.db import models
from pydantic import BaseModel

class CreateUser(BaseModel):
    name: str
    email: str
    journal_entries: null

