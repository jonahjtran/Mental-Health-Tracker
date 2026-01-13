import fastapi
from fastapi import Depends, HTTPException, Query, Path, status
from sqlalchemy.orm import Session
from backend.app.db.session import get_db
from backend.app.schemas.users import CreateUser, UserUpdate, UserRead
from backend.app.services.errors import ConflictError, NotFoundError
from backend.app.services.users_services import (
    create_user,
    get_user_by_id,
    get_user_by_name,
    get_user_by_email,
    update_user,
    delete_user,
)

router = fastapi.APIRouter()

@router.post("/users", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def create_user_endpoint(user_data: CreateUser, db: Session = Depends(get_db)):
    try:
        return create_user(db, user_data)
    except ConflictError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=exc.message,
        ) from exc

@router.get("/users/{user_id}", response_model=UserRead)
def get_user_by_id_endpoint(
    user_id: int = Path(..., ge=1), db: Session = Depends(get_db)
):
    try:
        return get_user_by_id(db, user_id)
    except NotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=exc.message,
        ) from exc

@router.delete("/users/{user_id}", response_model=UserRead)
def delete_user_endpoint(
    user_id: int = Path(..., ge=1), db: Session = Depends(get_db)
):
    try:
        return delete_user(db, user_id)
    except NotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=exc.message,
        ) from exc

@router.patch("/users/{user_id}", response_model=UserRead)
def update_user_endpoint(
    user_id: int = Path(..., ge=1),
    user_data: UserUpdate = ...,
    db: Session = Depends(get_db),
):
    try:
        return update_user(db, user_id, user_data)
    except NotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=exc.message,
        ) from exc

@router.get("/users/name/{name}", response_model=UserRead)
def get_user_by_name_endpoint(name: str, db: Session = Depends(get_db)):
    try:
        return get_user_by_name(db, name)
    except NotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=exc.message,
        ) from exc

@router.get("/users/by-email", response_model=UserRead)
def get_user_by_email_endpoint(email: str = Query(...), db: Session = Depends(get_db)):
    try:
        return get_user_by_email(db, email)
    except NotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=exc.message,
        ) from exc
