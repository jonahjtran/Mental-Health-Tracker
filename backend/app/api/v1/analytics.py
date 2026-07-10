from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from backend.app.core.security import get_current_user
from backend.app.db.session import get_db
from backend.app.schemas.analytics import AnalyticsOut
from backend.app.services.analytics_services import get_analytics
from backend.app.services.errors import NotFoundError

router = APIRouter(tags=["analytics"])


@router.get("/me/analytics", response_model=AnalyticsOut)
def get_analytics_endpoint(
    start_date: date = Query(None),
    end_date: date = Query(None),
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        return get_analytics(db, current_user.id, start_date=start_date, end_date=end_date)
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.message) from exc
