from backend.app.core.security import get_current_user
from backend.app.schemas.journal import JournalAnalysisOut, JournalAnalysisUpdate
from backend.app.services.insights_services import analyze_journal_entry, delete_insights
from backend.app.db.session import get_db
from backend.app.core.security import get_current_user
from backend.app.services.errors import NotFoundError
from backend.app.services.errors import NotFoundError
from backend.app.services.insights_services import delete_insights, update_insights, analyze_journal_entry, get_insights

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi import Path, Response



router = APIRouter(prefix="/api/v1/insights", tags=["insights"])

@router.post("/me/journals/{journal_id}/analyze", response_model=JournalAnalysisOut)
def analyze_journal_entry_endpoint(db: Session = Depends(get_db), journal_id: int = Path(..., ge=1), current_user = Depends(get_current_user)):
    try:
        return analyze_journal_entry(db, journal_id, current_user.id)
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.message) from exc

@router.get("/me/journals/{journal_id}/insights", response_model=JournalAnalysisOut)
def get_journal_insights_endpoint(db: Session = Depends(get_db), journal_id: int = Path(..., ge=1), current_user = Depends(get_current_user)):
    try:
        return get_insights(db, journal_id, current_user.id)
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.message) from exc

@router.delete("/me/journals/{journal_id}/insights", status_code=status.HTTP_204_NO_CONTENT)
def delete_journal_insights_endpoint(db: Session = Depends(get_db), journal_id: int = Path(..., ge=1), current_user = Depends(get_current_user)):
    try:
        return delete_insights(db, journal_id, current_user.id)
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.message) from exc
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)) from exc

@router.put("/me/journals/{journal_id}/insights", response_model=JournalAnalysisOut)
def update_journal_insights_endpoint(db: Session = Depends(get_db), journal_id: int = Path(..., ge=1), insights: JournalAnalysisUpdate = ..., current_user = Depends(get_current_user)):
    try:
        return update_insights(db, journal_id, current_user.id, insights)
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.message) from exc
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)) from exc

    
