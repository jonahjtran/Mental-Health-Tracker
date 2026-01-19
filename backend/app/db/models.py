from typing import List, Optional
from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import date, datetime
from .base import Base
from sqlalchemy.types import JSON



class Users(Base):
    __tablename__ = "users"

    id : Mapped[int] = mapped_column(primary_key=True)
    name : Mapped[str]
    email : Mapped[str]
    oauth_provider : Mapped[Optional[str]]
    oauth_subject: Mapped[Optional[str]]
    avatar_url: Mapped[Optional[str]]
    journal_entries : Mapped[List["Journal"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    insights : Mapped[List["JournalInsights"]] = relationship(back_populates="user", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"User(id={self.id!r}, name={self.name!r}, email={self.email!r})"
    
    
class Journal(Base):
    __tablename__ = "journal"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id : Mapped[int] = mapped_column(ForeignKey("users.id"))
    date: Mapped[date]
    mood_rating: Mapped[int]
    entry : Mapped[str]

    user : Mapped["Users"] = relationship(back_populates="journal_entries")
    insights : Mapped["JournalInsights"] = relationship(back_populates="journal", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"Journal(id={self.id!r}, user_id={self.user_id!r}, date={self.date!r}), mood_rating={self.mood_rating!r}, entry={self.entry!r})"

class JournalInsights(Base):
    __tablename__ = "journal_insights"

    id: Mapped[int] = mapped_column(primary_key=True)
    journal_id: Mapped[int] = mapped_column(ForeignKey("journal.id"), nullable=False, unique=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    summary: Mapped[str]
    themes: Mapped[List[str]] = mapped_column(JSON)
    sentiment: Mapped[dict] = mapped_column(JSON)
    suggestions: Mapped[List[str]] = mapped_column(JSON)
    risk_flag: Mapped[bool]
    risk_reason: Mapped[Optional[str]]
    model_name: Mapped[Optional[str]]
    created_at: Mapped[datetime] = mapped_column(default=datetime.now)

    journal: Mapped["Journal"] = relationship(back_populates="insights")
    user: Mapped["Users"] = relationship(back_populates="insights")

    def __repr__(self) -> str:
        return f"JournalInsights(id={self.id!r}, journal_id={self.journal_id!r}, user_id={self.user_id!r}, summary={self.summary!r}, themes={self.themes!r}, sentiment={self.sentiment!r}, suggestions={self.suggestions!r}, risk_flag={self.risk_flag!r}, risk_reason={self.risk_reason!r}, model_name={self.model_name!r}, created_at={self.created_at!r})"

