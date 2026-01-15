import fastapi
from fastapi import Depends, HTTPException, Path, Query, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.journal import JournalCreate, JournalRead, JournalUpdate
from app.services.errors import NotFoundError
from app.services.journal_services import (
    create_journal_entry,
    delete_journal_entry,
    get_journal_by_id,
    list_journal_entries,
    update_journal_entry,
)
from app.core.security import get_current_user
from typing import List
from datetime import date

router = fastapi.APIRouter()

@router.post("/me/journals", response_model=JournalRead, status_code=status.HTTP_201_CREATED,)
def create_journal_endpoint(
    journal_data: JournalCreate = ...,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        return create_journal_entry(db, current_user.id, journal_data)
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.message) from exc

@router.get("/me/journals/{journal_id}", response_model=JournalRead)
def get_journal_by_id_endpoint(
    journal_id: int = Path(..., ge=1),
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        return get_journal_by_id(db, current_user.id, journal_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.message) from exc

@router.get("/me/journals", response_model=List[JournalRead])
def get_journals_endpoint(
    date: date = Query(None),
    mood_rating: int = Query(None, ge=1, le=5),
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        return list_journal_entries(db, current_user.id, date=date, mood_rating=mood_rating)
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.message) from exc

@router.patch("/me/journals/{journal_id}", response_model=JournalRead)
def update_journal_endpoint(
    journal_id: int = Path(..., ge=1),
    journal_data: JournalUpdate = ...,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        return update_journal_entry(db, current_user.id, journal_id, journal_data)
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.message) from exc

@router.delete("/me/journals/{journal_id}", response_model=JournalRead)
def delete_journal_endpoint(
    journal_id: int = Path(..., ge=1),
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        return delete_journal_entry(db, current_user.id, journal_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.message) from exc
