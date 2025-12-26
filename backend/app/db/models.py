from typing import List
from typing import Optional
from sqlalchemy import ForeignKey
from sqlalchemy import String
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from datetime import date, datetime

class Base(DeclarativeBase):
    pass


class Users(Base):
    __tablename__ = "users"

    id : Mapped[int] = mapped_column(primary_key=True)
    name : Mapped[str]
    email : Mapped[str]
    journal_entries : Mapped[List["Journal"]] = relationship(back_populates="user", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"User(id={self.id!r}, name={self.name!r}, email={self.email!r})"
    
    
class Journal(Base):
    __tablename__ = "journal"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id : Mapped[int] = mapped_column(ForeignKey("users.id"))
    date: Mapped[datetime.date]
    mood_rating: Mapped[int]
    entry : Mapped[str]

    user : Mapped["Users"] = relationship(back_populates="journal_entries")

    def __repr__(self) -> str:
        return f"Journal(id={self.id!r}, user_id={self.user_id!r}, date={self.date!r}), mood_rating={self.mood_rating!r}, entry={self.entry!r})"
