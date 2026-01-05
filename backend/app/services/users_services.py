from csv import Error
from repositories.user_repository import create_user, get_user_by_email, get_user_by_id, update_user, delete_user, get_all_users, get_user_by_name, get_user_by_journal_entries, get_user_by_journal_entry_id, user_exists
from schemas.users import CreateUser, UserRead, UserUpdate, UserDelete
from schemas.journal import JournalRead
from sqlalchemy.orm import Session
from typing import List
from datetime import date

def create_user(db: Session, user_data: CreateUser):
    if user_data.name is None or user_data.email is None:
        return False, "Name and email are required"
    elif user_exists(db, user_data.email):
        return False, "User already exists"
    else:
        return create_user(db, user_data)

def get_user_by_email(db: Session, email: str):
    if get_user_by_email(db, email) is None:
        return False, "User does not exist"
    else:
        return get_user_by_email(db, email)
    
def update_user(db: Session, user_id: int, user_data: UserUpdate):
    if get_user_by_id(db, user_id) is None:
        return False, "User does not exist"
    
    update_user(db, user_id, user_data)
    return True, "Successfully updated user information"

def delete_user(db: Session, user_id: int):
    if get_user_by_id(db, user_id) is None:
        return False, "User does not exist"
    
    delete_user(db, user_id)
    return True, "Successfully deleted user"

def get_all_users(db: Session):
    return get_all_users(db)

def get_user_by_name(db: Session, name: str):
    if get_user_by_name(db, name) is None:
        return False, "User does not exist"

    return get_user_by_name(db, name)

def get_user_by_journal_entries(db: Session, journal_entries: List[JournalRead]):
    if get_user_by_journal_entries(db, journal_entries) is None:
        return False, "User does not exist"

    return get_user_by_journal_entries(db, journal_entries)

def get_user_by_journal_entry_id(db: Session, journal_entry_id: int):
    if get_user_by_journal_entry_id(db, journal_entry_id) is None:
        return False, "User does not exist"

def user_exists(db: Session, user_id: int):
    if user_exists(db, user_id) is False:
        return False, "User does not exist"

    return user_exists(db, user_id)