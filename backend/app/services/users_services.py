from repositories import user_repository
from schemas.users import CreateUser, UserRead, UserUpdate, UserDelete
from schemas.journal import JournalRead
from sqlalchemy.orm import Session
from typing import List
from datetime import date

def create_user(db: Session, user_data: CreateUser):
    if user_data.name is None or user_data.email is None:
        return False, "Name and email are required"
    elif user_repository.get_user_by_email(db, user_data.email) is not None:
        return False, "User already exists"
    else:
        return user_repository.create_user(db, user_data)

def get_user_by_email(db: Session, email: str):
    user = user_repository.get_user_by_email(db, email)
    if user is None:
        return False, "User does not exist"
    else:
        return user
    
def update_user(db: Session, user_id: int, user_data: UserUpdate):
    if user_repository.get_user_by_id(db, user_id) is None:
        return False, "User does not exist"
    
    user_repository.update_user(db, user_id, user_data)
    return True, "Successfully updated user information"

def delete_user(db: Session, user_id: int):
    if user_repository.get_user_by_id(db, user_id) is None:
        return False, "User does not exist"
    
    user_repository.delete_user(db, user_id)
    return True, "Successfully deleted user"

def get_all_users(db: Session):
    return user_repository.get_all_users(db)

def get_user_by_name(db: Session, name: str):
    user = user_repository.get_user_by_name(db, name)
    if user is None:
        return False, "User does not exist"

    return user

def get_user_by_journal_entries(db: Session, journal_entries: List[JournalRead]):
    users = user_repository.get_user_by_journal_entries(db, journal_entries)
    if users is None:
        return False, "User does not exist"

    return users

def get_user_by_journal_entry_id(db: Session, journal_entry_id: int):
    user = user_repository.get_user_by_journal_entry_id(db, journal_entry_id)
    if user is None:
        return False, "User does not exist"
    return user

def user_exists(db: Session, user_id: int):
    if user_repository.user_exists(db, user_id) is False:
        return False, "User does not exist"

    return user_repository.user_exists(db, user_id)
