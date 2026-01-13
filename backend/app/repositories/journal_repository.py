from datetime import date
from sqlalchemy.orm import Session
from db.models import Journal
from schemas.journal import JournalCreate, JournalRead, JournalUpdate

def create_journal(db: Session, user_id: int, journal_data):
    journal = Journal(
        user_id = user_id,
        date = journal_data.date,
        mood_rating = journal_data.mood_rating,
        entry = journal_data.entry
    )

    db.add(journal)
    db.commit()
    db.refresh(journal)
    return journal

# return all journals from a user
def get_journals_by_user(db: Session, user_id: int):
    return db.query(Journal).filter(Journal.user_id == user_id).all()

# return all journals from specific user on specific date
def get_journals_by_date(db: Session, user_id: int, date: date):
    return db.query(Journal).filter(Journal.user_id == user_id, Journal.date == date).all()

def delete_journal(db: Session, journal_id: int):
    db.query(Journal).filter(Journal.id == journal_id).delete()
    db.commit()
    return True

# TODO: test/verify correct function implementation
def get_journals_by_mood_rating(db: Session, mood_rating: int, user_id: int):
    return db.query(Journal).filter(Journal.user_id == user_id, Journal.mood_rating == mood_rating).all()

def update_journal(db: Session, journal_id: int, journal_data: JournalUpdate):
    update_data = journal_data.model_dump(exclude_unset=True)
    if update_data:
        db.query(Journal).filter(Journal.id == journal_id).update(update_data)
    db.commit()
    return get_journal_by_id(db, journal_id)

def get_journal_by_id(db: Session, journal_id: int):
    return db.query(Journal).filter(Journal.id == journal_id).first()

def get_journals_by_date(db: Session, user_id: int, date: date):
    return db.query(Journal).filter(Journal.user_id == user_id, Journal.date == date).all()

def get_journals_by_mood_rating(db: Session, user_id: int, mood_rating: int):
    return db.query(Journal).filter(Journal.user_id == user_id, Journal.mood_rating == mood_rating).all()

def get_journals_by_mood_rating_and_date(db: Session, user_id: int, mood_rating: int, date: date):
    return db.query(Journal).filter(Journal.user_id == user_id, Journal.mood_rating == mood_rating, Journal.date == date).all()
    
