from repositories import user_repository
from schemas.users import CreateUser, UserUpdate
from schemas.journal import JournalRead
from sqlalchemy.orm import Session
from typing import List

def create_user(db: Session, user_data: CreateUser):
    if user_data.name is None or user_data.email is None:
        return False
    elif user_repository.get_user_by_email(db, user_data.email) is not None:
        return False
    else:
        return user_repository.create_user(db, user_data)

def get_user_by_email(db: Session, email: str):
    user = user_repository.get_user_by_email(db, email)
    if user is None:
        return False
    return user

def get_user_by_id(db: Session, user_id: int):
    user = user_repository.get_user_by_id(db, user_id)
    if user is None:
        return False
    return user
    
def update_user(db: Session, user_id: int, user_data: UserUpdate):
    if user_repository.get_user_by_id(db, user_id) is None:
        return False
    
    user_repository.update_user(db, user_id, user_data)
    return user_repository.get_user_by_id(db, user_id)

def delete_user(db: Session, user_id: int):
    user = user_repository.get_user_by_id(db, user_id)
    if user is None:
        return False

    user_repository.delete_user(db, user_id)
    return user

def get_all_users(db: Session):
    return user_repository.get_all_users(db)

def get_user_by_name(db: Session, name: str):
    user = user_repository.get_user_by_name(db, name)
    if user is None:
        return False

    return user

def get_user_by_journal_entries(db: Session, journal_entries: List[JournalRead]):
    users = user_repository.get_user_by_journal_entries(db, journal_entries)
    if users is None:
        return False

    return users

def get_user_by_journal_entry_id(db: Session, journal_entry_id: int):
    user = user_repository.get_user_by_journal_entry_id(db, journal_entry_id)
    if user is None:
        return False
    return user

def user_exists(db: Session, user_id: int):
    if user_repository.user_exists(db, user_id) is False:
        return False

    return user_repository.user_exists(db, user_id)
