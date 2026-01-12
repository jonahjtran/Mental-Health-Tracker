import fastapi
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.users import CreateUser, UserUpdate, UserRead
from app.services.users_services import (
    create_user,
    get_user_by_id,
    get_user_by_name,
    get_user_by_email,
    update_user,
    delete_user,
)

router = fastapi.APIRouter()

@router.post("/users", response_model=UserRead)
def create_user_endpoint(user_data: CreateUser, db: Session = Depends(get_db)):
    user = create_user(db, user_data)
    if user is False:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user data or user already exists.",
        )
    return user

@router.get("/users/{user_id}", response_model=UserRead)
def get_user_by_id_endpoint(user_id: int, db: Session = Depends(get_db)):
    user = get_user_by_id(db, user_id)
    if user is False:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found.",
        )
    return user

@router.delete("/users/{user_id}", response_model=UserRead)
def delete_user_endpoint(user_id: int, db: Session = Depends(get_db)):
    user = delete_user(db, user_id)
    if user is False:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found.",
        )
    return user

@router.put("/users/{user_id}", response_model=UserRead)
def update_user_endpoint(user_id: int, user_data: UserUpdate, db: Session = Depends(get_db)):
    user = update_user(db, user_id, user_data)
    if user is False:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found.",
        )
    return user

@router.get("/users/name/{name}", response_model=UserRead)
def get_user_by_name_endpoint(name: str, db: Session = Depends(get_db)):
    user = get_user_by_name(db, name)
    if user is False:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found.",
        )
    return user

@router.get("/users/email/{email}", response_model=UserRead)
def get_user_by_email_endpoint(email: str, db: Session = Depends(get_db)):
    user = get_user_by_email(db, email)
    if user is False:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found.",
        )
    return user
