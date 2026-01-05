from csv import Error
import datetime
from logging import raiseExceptions
from repositories.journal_repository import create_journal, get_journals_by_user, get_journals_by_date, delete_journal, get_journals_by_mood_rating, update_journal, get_journal_by_id
from schemas.journal import JournalCreate, JournalRead

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
    
    create_journal(db, user_id, journal_data)
    return True


def delete_journal_entry(db: Session, journal_id: int):
    if get_journal_by_id(db, journal_id) is None:
        return False, "Journal entry does not exist"
    
    delete_journal(db, journal_id)
    return True




