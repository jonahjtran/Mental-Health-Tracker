from typing import List
from typing import Optional
from sqlalchemy import ForeignKey
from sqlalchemy import String
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
import users

class Base(DeclarativeBase):
    pass

class Journal(Base):
    __tablename__ = "journals"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id : Mapped[int] = mapped_column(ForeignKey("users.id"))
    date: Mapped[str]
    entry : Mapped[str]
    mood_rating: Mapped[int]
