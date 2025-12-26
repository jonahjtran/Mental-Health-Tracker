# File Structure
backend/
├── app/
│   ├── main.py                  # App entry point
│   ├── api/
│   │   ├── __init__.py
│   │   ├── v1/
│   │   │   ├── __init__.py
│   │   │   ├── health.py         # Health check
│   │   │   ├── users.py          # User-related endpoints
│   │   │   ├── journals.py       # Journaling endpoints
│   │   │   ├── insights.py       # AI/ML endpoints
│   │
│   ├── core/
│   │   ├── config.py             # Environment variables
│   │   ├── security.py           # Auth, JWT, hashing
│   │   ├── logging.py
│   │
│   ├── db/
│   │   ├── base.py               # SQLAlchemy Base
│   │   ├── session.py            # DB session
│   │   ├── init_db.py
│   │   ├── models.py
│   │
│   ├── schemas/
│   │   ├── user.py               # Pydantic schemas
│   │   ├── journal.py
│   │   ├── insight.py
│   │
│   ├── repositories/
│   │   ├── user_repo.py          # DB queries
│   │   ├── journal_repo.py
│   │
│   ├── services/
│   │   ├── user_service.py       # Business logic
│   │   ├── journal_service.py
│   │   ├── insight_service.py
│   │
│   ├── ai/
│   │   ├── model.py              # AI model wrapper
│   │   ├── embeddings.py
│   │   ├── inference.py
│   │
│   ├── utils/
│   │   ├── text.py
│   │   ├── time.py
│
├── tests/
│   ├── test_users.py
│   ├── test_journals.py
│
├── alembic/                      # DB migrations
├── .env
├── requirements.txt
└── README.md
