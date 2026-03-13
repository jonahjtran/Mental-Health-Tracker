import sys
from pathlib import Path

from sqlalchemy import create_engine, inspect


ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from backend.app.db import init_db


def test_init_db_creates_expected_tables(monkeypatch) -> None:
    engine = create_engine("sqlite+pysqlite:///:memory:", future=True)
    monkeypatch.setattr(init_db, "engine", engine)

    init_db.init_db()

    tables = set(inspect(engine).get_table_names())
    assert {"users", "journal", "journal_insights"} <= tables
