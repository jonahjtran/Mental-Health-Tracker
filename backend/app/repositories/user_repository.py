from sqlalchemy.orm import Session
from app import db
from app.db.models import Users, Journal
from app.schemas.users import CreateUser, UserRead, UserUpdate, UserDelete
from app.schemas.journal import JournalRead
from typing import List, Optional

def create_user(db: Session, user_data: CreateUser):
    user = Users(
        name = user_data.name,
        email = user_data.email,
        journal_entries = user_data.journal_entries
    )

    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def user_exists(db: Session, user_id: int):
    if db.query(Users).filter(Users.id == user_id).first() is not None:
        return True
    return False

def get_user_by_email(db: Session, email: str):
    return db.query(Users).filter(Users.email == email).first()

def get_user_by_id(db: Session, user_id: int):
    return db.query(Users).filter(Users.id == user_id).first()

def update_user(db: Session, user_id: int, user_data: UserUpdate):
    print("inside update user function")
    db.query(Users).filter(Users.id == user_id).update(user_data.model_dump(exclude={"journal_entries"}))
    db.commit()
    print("committed update user function")
    return True

def delete_user(db: Session, user_id: int):
    db.query(Users).filter(Users.id == user_id).delete()
    db.commit()
    return True

def get_all_users(db: Session):
    return db.query(Users).all()

def get_user_by_name(db: Session, name: str):
    return db.query(Users).filter(Users.name == name).first()

def get_user_by_journal_entries(db: Session, journal_entries: List[JournalRead]):
    return db.query(Users).filter(Users.journal_entries == journal_entries).all()

def get_user_by_journal_entry_id(db: Session, journal_entry_id: int):
    return db.query(Users).filter(Users.journal_entries.any(Journal.id == journal_entry_id)).first()

def get_user_by_oauth(db: Session, provider: str, subject: str):
    return db.query(Users).filter(Users.oauth_provider == provider, Users.oauth_subject == subject).first()

def create_oauth_user(db: Session, provider: str, subject: str, email: str, name: str, avatar_url: Optional[str] = None):
    user = Users(
        oauth_provider = provider,
        oauth_subject = subject,
        email = email,
        name = name,
        avatar_url = avatar_url,
    )

    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def link_oauth_identity(db: Session, user_id: int, provider: str, subject: str, avatar_url: Optional[str] = None):
    db.query(Users).filter(Users.id == user_id).update(
        {
            Users.oauth_provider: provider,
            Users.oauth_subject: subject,
            Users.avatar_url: avatar_url,
        }
    )
    db.commit()
    return db.query(Users).filter(Users.id == user_id).first()
