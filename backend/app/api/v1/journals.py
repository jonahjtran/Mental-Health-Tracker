import fastapi
from fastapi import Depends, HTTPException, Path, Query, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.journal import JournalCreate, JournalRead, JournalUpdate
from app.services.journal_services import (
    create_journal_entry,
    delete_journal_entry,
    get_journal_by_date,
    get_journal_by_id,
    get_journal_by_mood_rating,
    get_journals_by_user,
    update_journal_entry,
)
from typing import List
from datetime import date

router = fastapi.APIRouter()

@router.post("/journals/create/{user_id}", response_model=JournalRead, status_code=status.HTTP_201_CREATED)
def create_journal_endpoint(
    user_id: int, journal_data: JournalCreate, db: Session = Depends(get_db)
):
    return create_journal_entry(db, user_id, journal_data)

@router.get("/journals/id/{journal_id}", response_model=JournalRead)
def get_journal_by_id_endpoint(
    journal_id: int, user_id: int, db: Session = Depends(get_db)
):
    journal = get_journal_by_id(db, user_id, journal_id)
    if journal is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Journal not found")
    return journal

@router.get("/journals/date/{date}", response_model=List[JournalRead])
def get_journal_by_date_endpoint(
    date: date, user_id: int, db: Session = Depends(get_db)
):
    return get_journal_by_date(db, user_id, date)

@router.get("/journals/user/{user_id}", response_model=List[JournalRead])
def get_journal_by_user_endpoint(user_id: int, db: Session = Depends(get_db)):
    return get_journals_by_user(db, user_id)

@router.get("/journals/mood/{mood_rating}", response_model=List[JournalRead])
def get_journal_by_mood_rating_endpoint(
    mood_rating: int = Path(..., ge=1, le=5),
    user_id: int = Query(...),
    db: Session = Depends(get_db),
):
    return get_journal_by_mood_rating(db, user_id, mood_rating)

@router.put("/journals/update/{journal_id}", response_model=JournalRead)
def update_journal_endpoint(
    journal_id: int, journal_data: JournalUpdate, db: Session = Depends(get_db)
):
    journal = update_journal_entry(db, journal_id, journal_data)
    if journal is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Journal not found")
    return journal

@router.delete("/journals/delete/{journal_id}", response_model=JournalRead)
def delete_journal_endpoint(journal_id: int, db: Session = Depends(get_db)):
    journal = delete_journal_entry(db, journal_id)
    if journal is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Journal not found")
    return journal
