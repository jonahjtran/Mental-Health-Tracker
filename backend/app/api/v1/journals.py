import fastapi
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.journal import JournalCreate, JournalRead, JournalUpdate
from app.services.journal_services import create_journal_entry, get_journal_by_id, get_journal_by_date, get_journals_by_user, update_journal_entry, delete_journal_entry, get_journal_by_mood_rating
from typing import List
from datetime import date

router = fastapi.APIRouter()

@router.post("/journals", response_model=JournalRead)
def create_journal_endpoint(journal_data: JournalCreate, db: Session = Depends(get_db)):
    return create_journal_entry(db, journal_data)

@router.get("/journals/id/{journal_id}", response_model=JournalRead)
def get_journal_by_id_endpoint(journal_id: int, db: Session = Depends(get_db)):
    return get_journal_by_id(db, journal_id)

@router.get("/journals/data/{date}", response_model=List[JournalRead])
def get_journal_by_date_endpoint(
    data: date, user_id: int, db: Session = Depends(get_db)
):
    return get_journal_by_date(db, user_id, data)

@router.get("/journals/user/{user_id}", response_model=List[JournalRead])
def get_journal_by_user_endpoint(user_id: int, db: Session = Depends(get_db)):
    return get_journals_by_user(db, user_id)

@router.get("/journals/mood/{mood_rating}", response_model=List[JournalRead])
def get_journal_by_mood_rating_endpoint(
    mood_rating: int, user_id: int, db: Session = Depends(get_db)
):
    return get_journal_by_mood_rating(db, user_id, mood_rating)

@router.put("/journals/update/{journal_id}", response_model=JournalUpdate)
def update_journal_endpoint(journal_id: int, journal_data: JournalUpdate, db: Session = Depends(get_db)):
    return update_journal(db, journal_id, journal_data)

@router.delete("/journals/delete/{journal_id}", response_model=JournalRead)
def delete_journal_endpoint(journal_id: int, db: Session = Depends(get_db)):
    return delete_journal(db, journal_id)
