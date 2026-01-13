from csv import Error
import datetime
from logging import raiseExceptions
from backend.app.repositories.user_repository import user_exists
from repositories.journal_repository import (
    create_journal as repo_create_journal,
    delete_journal as repo_delete_journal,
    get_journal_by_id as repo_get_journal_by_id,
    get_journals_by_date as repo_get_journals_by_date,
    get_journals_by_mood_rating as repo_get_journals_by_mood_rating,
    get_journals_by_mood_rating_and_date as repo_get_journals_by_mood_rating_and_date,
    get_journals_by_user as repo_get_journals_by_user,
    update_journal as repo_update_journal,
)
from schemas.journal import JournalCreate, JournalRead, JournalUpdate

from sqlalchemy.orm import Session
from typing import List
from datetime import date


def create_journal_entry(db: Session, user_id: int, journal_data: JournalCreate):
    if user_id != journal_data.user_id:
        return False, "User ID does not match"
    elif journal_data.mood_rating is None:
        return False, "Mood rating is required" # later change to ai sentiment analysis
    elif journal_data.mood_rating < 1 or journal_data.mood_rating > 5:
        return False, "Mood rating must be between 1 and 5"
    elif journal_data.entry is None:
        return False, "Entry is required"

    if journal_data.date is None:
        journal_data.date = date.today()
    
    return repo_create_journal(db, user_id, journal_data)


def delete_journal_entry(db: Session, journal_id: int):
    if repo_get_journal_by_id(db, journal_id) is None:
        return False, "Journal entry does not exist"
    
    repo_delete_journal(db, journal_id)
    return True

def update_journal_entry(db: Session, journal_id: int, journal_data: JournalUpdate):
    if repo_get_journal_by_id(db, journal_id) is None:
        return False, "Journal entry does not exist"

    repo_update_journal(db, journal_id, journal_data)
    return True

def list_journal_entries(db: Session, user_id: int, *, date: date = None, mood_rating: int = None):
    if user_exists(db, user_id) is False:
        return False, "User does not exist"

    if date is not None and mood_rating is not None:
        return repo_get_journals_by_mood_rating_and_date(db, user_id, mood_rating, date)
    elif date is not None:
        return repo_get_journals_by_date(db, user_id, date)
    elif mood_rating is not None:
        return repo_get_journals_by_mood_rating(db, user_id, mood_rating)
    else:
        return repo_get_journals_by_user(db, user_id)

def get_journal_by_id(db: Session, user_id: int, journal_id: int):
    if repo_get_journal_by_id(db, journal_id) is None:
        return False, "Journal does not exist"
    elif repo_get_journal_by_id(db, journal_id).user_id != user_id:
        return False, "Journal does not match user"

    return repo_get_journal_by_id(db, journal_id)

def get_journal_by_date(db: Session, user_id: int, date: date):
    return repo_get_journals_by_date(db, user_id, date)

def get_journal_by_mood_rating(db: Session, user_id: int, mood_rating: int):
    if mood_rating < 1 or mood_rating > 5:
        return False, "Mood rating must be between 1 and 5"

    return repo_get_journals_by_mood_rating(db, user_id, mood_rating)


def get_journals_by_user(db: Session, user_id: int):
    return repo_get_journals_by_user(db, user_id)





