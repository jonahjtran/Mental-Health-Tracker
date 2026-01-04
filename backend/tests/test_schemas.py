import sys
from pathlib import Path
from datetime import date

import pytest
from pydantic import ValidationError


# Ensure both project root and backend/ are on the import path for schema imports.
ROOT_DIR = Path(__file__).resolve().parents[2]
BACKEND_DIR = ROOT_DIR / "backend"
for path in (ROOT_DIR, BACKEND_DIR):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from backend.app.schemas.journal import JournalCreate, JournalRead, JournalUpdate
from backend.app.schemas.users import CreateUser, UserRead, UserUpdate


def test_journal_create_accepts_valid_payload() -> None:
    payload = JournalCreate(date=date(2024, 1, 1), mood_rating=3, entry="Ok day.")

    assert payload.date == date(2024, 1, 1)
    assert payload.mood_rating == 3
    assert payload.entry == "Ok day."


@pytest.mark.parametrize("rating", [0, 6])
def test_journal_read_rejects_out_of_range_mood_rating(rating: int) -> None:
    with pytest.raises(ValidationError):
        JournalRead(
            id=1,
            date=date(2024, 1, 1),
            mood_rating=rating,
            entry="Testing bounds.",
        )


def test_journal_update_requires_mood_rating() -> None:
    with pytest.raises(ValidationError):
        JournalUpdate(entry="Only updating entry.")


def test_create_user_accepts_empty_journal_entries() -> None:
    payload = CreateUser(name="Alex", email="alex@example.com", journal_entries=[])

    assert payload.name == "Alex"
    assert payload.email == "alex@example.com"
    assert payload.journal_entries == []


def test_user_read_accepts_nested_journal_entries() -> None:
    payload = UserRead(
        id=10,
        name="Riley",
        email="riley@example.com",
        journal_entries=[
            {
                "id": 5,
                "date": date(2024, 1, 2),
                "mood_rating": 4,
                "entry": "Solid day.",
            }
        ],
    )

    assert payload.id == 10
    assert payload.journal_entries[0].mood_rating == 4


def test_user_update_allows_partial_updates() -> None:
    payload = UserUpdate(email="new@example.com")

    assert payload.name is None
    assert payload.email == "new@example.com"
