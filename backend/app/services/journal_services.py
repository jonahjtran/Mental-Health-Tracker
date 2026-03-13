from backend.app.repositories.user_repository import user_exists
from backend.app.repositories.journal_repository import (
    create_journal as repo_create_journal,
    delete_journal as repo_delete_journal,
    get_journal_by_id as repo_get_journal_by_id,
    get_journals_by_date as repo_get_journals_by_date,
    get_journals_by_mood_rating as repo_get_journals_by_mood_rating,
    get_journals_by_mood_rating_and_date as repo_get_journals_by_mood_rating_and_date,
    get_journals_by_user as repo_get_journals_by_user,
    update_journal as repo_update_journal,
)
from backend.app.schemas.journal import JournalCreate, JournalRead, JournalUpdate
from backend.app.services.errors import NotFoundError

from sqlalchemy.orm import Session
from datetime import date


def create_journal_entry(db: Session, user_id: int, journal_data: JournalCreate):
    if user_exists(db, user_id) is False:
        raise NotFoundError("User not found.")
    return repo_create_journal(db, user_id, journal_data)


def delete_journal_entry(db: Session, user_id: int, journal_id: int):
    journal = repo_get_journal_by_id(db, journal_id)
    if journal is None or journal.user_id != user_id:
        raise NotFoundError("Journal not found.")

    journal_read = JournalRead.model_validate(journal)
    repo_delete_journal(db, journal_id)
    return journal_read

def update_journal_entry(db: Session, user_id: int, journal_id: int, journal_data: JournalUpdate):
    journal = repo_get_journal_by_id(db, journal_id)
    if journal is None or journal.user_id != user_id:
        raise NotFoundError("Journal not found.")

    return repo_update_journal(db, journal_id, journal_data)

def list_journal_entries(db: Session, user_id: int, *, date: date = None, mood_rating: int = None):
    if user_exists(db, user_id) is False:
        raise NotFoundError("User not found.")

    if date is not None and mood_rating is not None:
        return repo_get_journals_by_mood_rating_and_date(db, user_id, mood_rating, date)
    elif date is not None:
        return repo_get_journals_by_date(db, user_id, date)
    elif mood_rating is not None:
        return repo_get_journals_by_mood_rating(db, user_id, mood_rating)
    else:
        return repo_get_journals_by_user(db, user_id)

def get_journal_by_id(db: Session, user_id: int, journal_id: int):
    journal = repo_get_journal_by_id(db, journal_id)
    if journal is None or journal.user_id != user_id:
        raise NotFoundError("Journal not found.")
    return journal

def get_journal_by_date(db: Session, user_id: int, date: date):
    if user_exists(db, user_id) is False:
        raise NotFoundError("User not found.")
    return repo_get_journals_by_date(db, user_id, date)

def get_journal_by_mood_rating(db: Session, user_id: int, mood_rating: int):
    if user_exists(db, user_id) is False:
        raise NotFoundError("User not found.")
    return repo_get_journals_by_mood_rating(db, user_id, mood_rating)


def get_journals_by_user(db: Session, user_id: int):
    if user_exists(db, user_id) is False:
        raise NotFoundError("User not found.")
    return repo_get_journals_by_user(db, user_id)
