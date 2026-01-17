from backend.app.core.security import get_current_user
from backend.app.schemas.journal import JournalAnalysisOut
from backend.app.services.insights_services import analyze_journal_entry
from backend.app.db.session import get_db
from backend.app.core.security import get_current_user


from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi import Path
from backend.app.services.errors import NotFoundError
from backend.app.repositories.insights_repository import get_existing_insights




router = APIRouter(prefix="/api/v1/insights", tags=["insights"])

@router.post("/me/journals/{journal_id}/analyze", response_model=JournalAnalysisOut)
def analyze_journal_entry_endpoint(db: Session = Depends(get_db), journal_id: int = Path(..., ge=1)):
    try:
        return analyze_journal_entry(db, journal_id,Depends(get_current_user))
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.message) from exc

@router.get("/me/journals/{journal_id}/insights", response_model=JournalAnalysisOut)
def get_journal_insights_endpoint(db: Session = Depends(get_db), journal_id: int = Path(..., ge=1)):
    try:
        return get_existing_insights(db, journal_id,Depends(get_current_user))
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.message) from exc

@router.delete("/me/journals/{journal_id}/insihgts", status_code=status.HTTP_204_NO_CONTENT)
def delete_journal_insights_endpoint(db: Session = Depends(get_db), journal_id: int = Path(..., ge=1)):
    try:
        delete_insights