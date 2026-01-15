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
from backend.app.core.security import get_current_user

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
    user_id: int = Path(..., ge=1),
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    try:
        return get_user_by_id(db, user_id)
    except NotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=exc.message,
        ) from exc

@router.get("/me", response_model=UserRead)
def get_me_endpoint(current_user = Depends(get_current_user)):
    return current_user

@router.delete("/users/{user_id}", response_model=UserRead)
def delete_user_endpoint(
    user_id: int = Path(..., ge=1),
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    try:
        return delete_user(db, user_id)
    except NotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=exc.message,
        ) from exc

@router.delete("/me", response_model=UserRead)
def delete_me_endpoint(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        return delete_user(db, current_user.id)
    except NotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=exc.message,
        ) from exc

@router.patch("/users/{user_id}", response_model=UserRead)
def update_user_endpoint(
    user_id: int = Path(..., ge=1),
    user_data: UserUpdate = ...,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    try:
        return update_user(db, user_id, user_data)
    except NotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=exc.message,
        ) from exc

@router.patch("/me", response_model=UserRead)
def update_me_endpoint(
    user_data: UserUpdate = ...,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        return update_user(db, current_user.id, user_data)
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
