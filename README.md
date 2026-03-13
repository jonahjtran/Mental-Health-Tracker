# Mental Health Tracker API

A backend-focused mental health journaling platform built with FastAPI, SQLAlchemy, JWT auth, Google OAuth, and AI-generated journal insights.

This project is designed around a clean service architecture: API routes stay thin, business logic lives in services, persistence lives in repositories, and the data model is backed by PostgreSQL-compatible infrastructure such as Supabase.

## Why This Project Stands Out

- Built a production-style FastAPI backend with layered architecture instead of a single-file CRUD demo.
- Integrated Google OAuth for sign-in and JWT-based session authentication for protected routes.
- Added AI-powered journal analysis that generates summaries, themes, sentiment, suggestions, and risk flags from freeform journal entries.
- Structured the project for testability with repository, service, schema, API, and startup tests.
- Configured the app to create database tables on startup for rapid deployment to hosted PostgreSQL environments.

## Features

- User creation and profile management
- Google OAuth login flow
- JWT cookie authentication
- Journal CRUD endpoints scoped to the authenticated user
- AI insights generation for journal entries
- Health check endpoint
- Swagger/OpenAPI docs via `/docs`

## Tech Stack

- Python
- FastAPI
- SQLAlchemy ORM
- Pydantic
- PostgreSQL / Supabase
- Authlib
- PyJWT
- Google GenAI
- Pytest

## API Surface

Main routes currently exposed under `/api/v1`:

- `/health`
- `/users`
- `/users/{user_id}`
- `/users/by-email`
- `/me`
- `/me/journals`
- `/me/journals/{journal_id}`
- `/auth/login/google`
- `/auth/callback/google`
- `/auth/logout`
- `/insights/me/journals/{journal_id}/analyze`
- `/insights/me/journals/{journal_id}/insights`

Interactive docs are available at:

```text
http://127.0.0.1:8000/docs
```

## Architecture

```text
backend/app
├── api/v1          # FastAPI route handlers
├── core            # settings and auth/security
├── db              # models, engine, startup init
├── repositories    # database access layer
├── schemas         # request/response models
├── services        # business logic
└── ai              # prompt template for insights
```

## Example Workflow

1. Create a user.
2. Authenticate through Google OAuth or a JWT-based flow.
3. Create journal entries tied to the signed-in user.
4. Request AI analysis for a journal entry.
5. Read generated themes, sentiment, summary, suggestions, and risk flag output.

## Local Setup

1. Create and activate a virtual environment.
2. Install dependencies:

```bash
pip install -r backend/requirements.txt
```

3. Configure environment variables in `.env` or `backend/.env`:

```env
DATABASE_URL=postgresql://...
JWT_SECRET=your_secret
JWT_EXPIRES_MINUTES=60
GOOGLE_CLIENT_ID=...
GOOGLE_CLIENT_SECRET=...
GOOGLE_REDIRECT_URI=http://localhost:8000/api/v1/auth/callback/google
FRONTEND_URL=http://localhost:3000
INSIGHTS_API_KEY=...
INSIGHTS_MODEL=gemini-2.5-flash
```

4. Start the API from the repository root:

```bash
uvicorn backend.app.main:app --reload
```

5. Open:

```text
http://127.0.0.1:8000/docs
```

## Testing

Run the backend test suite:

```bash
pytest backend/tests -q
```

The project currently includes test coverage for:

- database models and relationships
- repositories
- services
- API endpoints
- OAuth flow behavior
- startup wiring and table creation

## What I Built

- Designed the backend architecture and data model for users, journal entries, and AI insights.
- Implemented authenticated journaling endpoints with user scoping.
- Added database initialization for hosted PostgreSQL deployments.
- Wrote automated tests to validate the application layers and startup path.
- Integrated LLM-based analysis into a REST API workflow.
