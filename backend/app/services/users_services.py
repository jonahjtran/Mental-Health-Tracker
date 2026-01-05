from csv import Error
from repositories.user_repository import create_user, get_user_by_email, get_user_by_id, update_user, delete_user, get_all_users, get_user_by_name, get_user_by_journal_entries, get_user_by_journal_entry_id, user_exists
from schemas.users import CreateUser, UserRead, UserUpdate, UserDelete
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

def get_user