import fastapi
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.users import CreateUser, UserUpdate, UserDelete, UserRead
from app.services.users_services import create_user, get_user_by_email, update_user, delete_user, get_all_users, get_user_by_name, get_user_by_journal_entries, get_user_by_journal_entry_id, user_exists, get_user_by_id, get_user_by_name, get_user_by_email

from typing import List

router = fastapi.APIRouter()

@router.post("/users", response_model=UserRead)
def create_user_endpoint(user_data: CreateUser, db: Session = Depends(get_db)):
    return create_user(db, user_data)

@router.get("/users", response_model=List[UserRead])
def get_user_by_id_endpoint(user_id: int, db: Session = Depends(get_db)):
    return get_user_by_id(db, user_id)

@router.delete("/users/{user_id}", response_model=UserRead)
def delete_user_endpoint(user_id: int, db: Session = Depends(get_db)):
    return delete_user(db, user_id)

@router.put("/users/{user_id}", response_model=UserRead)
def update_user_endpoint(user_id: int, user_data: UserUpdate, db: Session = Depends(get_db)):
    return update_user(db, user_id, user_data)

@router.get("/users/name/{name}", response_model=List[UserRead])
def get_user_by_name_endpoint(name: str, db: Session = Depends(get_db)):
    return get_user_by_name(db, name)

@router.get("/users/email/{email}", response_model=List[UserRead])
def get_user_by_email_endpoint(email: str, db: Session = Depends(get_db)):
    return get_user_by_email(db, email)