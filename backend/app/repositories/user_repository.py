from sqlalchemy.orm import Session
from db.models import Users
from schemas.users import CreateUser, UserRead, UserUpdate, UserDelete
from schemas.journal import JournalRead
from typing import List
from db.models import Journal

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

def get_user_by_email(db: Session, email: str):
    return db.query(Users).filter(Users.email == email).first()

def get_user_by_id(db: Session, user_id: int):
    return db.query(Users).filter(Users.id == user_id).first()

def update_user(db: Session, user_id: int, user_data: UserUpdate):
    db.query(Users).filter(Users.id == user_id).update(user_data.model_dump())
    db.commit()
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