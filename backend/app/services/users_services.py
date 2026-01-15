from backend.app.repositories import user_repository
from backend.app.schemas.users import CreateUser, UserUpdate
from backend.app.schemas.journal import JournalRead
from backend.app.services.errors import ConflictError, NotFoundError
from sqlalchemy.orm import Session
from typing import List, Optional


def create_user(db: Session, user_data: CreateUser):
    if user_repository.get_user_by_email(db, user_data.email) is not None:
        raise ConflictError("User already exists.")
    return user_repository.create_user(db, user_data)

def get_user_by_email(db: Session, email: str):
    user = user_repository.get_user_by_email(db, email)
    if user is None:
        raise NotFoundError("User not found.")
    return user

def get_user_by_id(db: Session, user_id: int):
    user = user_repository.get_user_by_id(db, user_id)
    if user is None:
        raise NotFoundError("User not found.")
    return user
    
def update_user(db: Session, user_id: int, user_data: UserUpdate):
    if user_repository.get_user_by_id(db, user_id) is None:
        raise NotFoundError("User not found.")
    
    user_repository.update_user(db, user_id, user_data)
    return user_repository.get_user_by_id(db, user_id)

def delete_user(db: Session, user_id: int):
    user = user_repository.get_user_by_id(db, user_id)
    if user is None:
        raise NotFoundError("User not found.")

    user_repository.delete_user(db, user_id)
    return user

def get_all_users(db: Session):
    return user_repository.get_all_users(db)

def get_user_by_name(db: Session, name: str):
    user = user_repository.get_user_by_name(db, name)
    if user is None:
        raise NotFoundError("User not found.")
    return user

def get_user_by_journal_entries(db: Session, journal_entries: List[JournalRead]):
    users = user_repository.get_user_by_journal_entries(db, journal_entries)
    return users

def get_user_by_journal_entry_id(db: Session, journal_entry_id: int):
    user = user_repository.get_user_by_journal_entry_id(db, journal_entry_id)
    if user is None:
        raise NotFoundError("User not found.")
    return user

def user_exists(db: Session, user_id: int):
    return user_repository.user_exists(db, user_id)

def get_or_create_user_from_oauth(db: Session, provider: str, subject: str, email: str, name: str, avatar_url: Optional[str] = None):
    user = user_repository.get_user_by_oauth(db, provider, subject)
    if user is not None:
        return user
    
    existing = user_repository.get_user_by_email(db, email) is not None:
    
    if existing is not None:
        return user_repository.link_oauth_identity(db, user_id = existing.id, provider = provider, subject = subject, avatar_url=avatar_url)
    
    return user_repository.create_oauth_user(db, provider, subject, email, name, avatar_url)