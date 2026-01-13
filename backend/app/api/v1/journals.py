import fastapi
from fastapi import Depends, HTTPException, Path, Query, status
from sqlalchemy.orm import Session
from backend.app.db.session import get_db
from backend.app.schemas.journal import JournalCreate, JournalRead, JournalUpdate
from backend.app.services.errors import NotFoundError
from backend.app.services.journal_services import (
    create_journal_entry,
    delete_journal_entry,
    get_journal_by_id,
    list_journal_entries,
    update_journal_entry,
)
from typing import List
from datetime import date

router = fastapi.APIRouter()

@router.post(
    "/users/{user_id}/journals",
    response_model=JournalRead,
    status_code=status.HTTP_201_CREATED,
)
def create_journal_endpoint(
    user_id: int = Path(..., ge=1),
    journal_data: JournalCreate = ...,
    db: Session = Depends(get_db),
):
    try:
        return create_journal_entry(db, user_id, journal_data)
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.message) from exc

@router.get("/users/{user_id}/journals/{journal_id}", response_model=JournalRead)
def get_journal_by_id_endpoint(
    user_id: int = Path(..., ge=1),
    journal_id: int = Path(..., ge=1),
    db: Session = Depends(get_db),
):
    try:
        return get_journal_by_id(db, user_id, journal_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.message) from exc

@router.get("/users/{user_id}/journals", response_model=List[JournalRead])
def get_journals_endpoint(
    user_id: int = Path(..., ge=1),
    date: date = Query(None),
    mood_rating: int = Query(None, ge=1, le=5),
    db: Session = Depends(get_db),
):
    try:
        return list_journal_entries(db, user_id, date=date, mood_rating=mood_rating)
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.message) from exc

@router.patch("/users/{user_id}/journals/{journal_id}", response_model=JournalRead)
def update_journal_endpoint(
    user_id: int = Path(..., ge=1),
    journal_id: int = Path(..., ge=1),
    journal_data: JournalUpdate = ...,
    db: Session = Depends(get_db),
):
    try:
        return update_journal_entry(db, user_id, journal_id, journal_data)
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.message) from exc

@router.delete("/users/{user_id}/journals/{journal_id}", response_model=JournalRead)
def delete_journal_endpoint(
    user_id: int = Path(..., ge=1),
    journal_id: int = Path(..., ge=1),
    db: Session = Depends(get_db),
):
    try:
        return delete_journal_entry(db, user_id, journal_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.message) from exc
