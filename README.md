# Mental Health Tracker API

Backend for a mental-health journaling platform: **FastAPI**, **SQLAlchemy**, **JWT auth**, **Google OAuth**, and AI-generated journal insights. Built with an industry-style layered architecture (API → services → repositories → DB) and RESTful design.

---

## Resume Highlights (Google XYZ)

- **FastAPI & REST API:** Delivered **23 REST API endpoints** across 5 resource areas (health, auth, users, journals, insights), by building the backend with FastAPI, versioned routers under `/api/v1`, thin route handlers, Pydantic request/response schemas, and consistent HTTP semantics (GET/POST/PATCH/PUT/DELETE) with appropriate status codes.

- **Industry-level structure:** Achieved clear separation of concerns with **3 repository modules**, **3 service modules**, **5 API route modules**, **3 SQLAlchemy models**, and **12+ Pydantic schemas**, by keeping routes as thin adapters, business logic in services, persistence in repositories, and type-safe contracts in schemas.

- **JWT authentication:** Secured protected routes with **JWT tokenization** (HS256, configurable expiration), by implementing token creation, extraction from `Authorization: Bearer` header and `access_token` cookie, a `get_current_user` dependency that validates tokens and loads the user, and `verify_token` for server-side checks.

---

## Tech Stack

| Layer        | Technologies |
|-------------|--------------|
| API         | FastAPI, Pydantic |
| Auth        | PyJWT (HS256), Authlib (Google OAuth) |
| Data        | SQLAlchemy ORM, PostgreSQL / Supabase |
| AI          | Google GenAI (insights) |
| Testing     | Pytest, pytest-cov, pytest-mock, pytest-asyncio |

---

## Architecture

```
backend/app
├── api/v1/          # REST route handlers (thin; delegate to services)
├── core/            # config, JWT & security (create_access_token, get_current_user)
├── db/              # SQLAlchemy models, engine, session, init_db
├── repositories/    # data access (user, journal, insights)
├── schemas/         # Pydantic request/response models
├── services/        # business logic (users, journals, insights)
└── ai/              # prompt template for LLM insights
```

- **Models:** `Users`, `Journal`, `JournalInsights` (relationships, FKs, JSON columns for themes/sentiment).
- **Schemas:** Create/Read/Update and analysis DTOs in `schemas/users.py` and `schemas/journal.py`.
- **Services:** User lifecycle, journal CRUD, and insights (analyze, get, update, delete) with clear error handling.

---

## API Surface (`/api/v1`)

| Area    | Endpoints |
|---------|-----------|
| Health  | `GET /health` |
| Auth    | `GET /auth/login/google`, `GET /auth/callback/google`, `POST /auth/logout`, `GET /auth/logout` |
| Users   | `POST /users`, `GET /users/{id}`, `GET /me`, `PATCH /users/{id}`, `PATCH /me`, `DELETE /users/{id}`, `DELETE /me`, `GET /users/name/{name}`, `GET /users/by-email` |
| Journals| `POST /me/journals`, `GET /me/journals`, `GET /me/journals/{id}`, `PATCH /me/journals/{id}`, `DELETE /me/journals/{id}` |
| Insights| `POST /me/journals/{id}/analyze`, `GET /me/journals/{id}/insights`, `PUT /me/journals/{id}/insights`, `DELETE /me/journals/{id}/insights` |

**Total: 23 REST endpoints.** Interactive docs: `http://127.0.0.1:8000/docs`.

---

## Features

- User creation and profile management (CRUD, by-id, by-email)
- Google OAuth login and JWT cookie/Bearer authentication
- Journal CRUD scoped to the authenticated user (`/me/journals`)
- AI-generated insights (summary, themes, sentiment, suggestions, risk flag) for journal entries
- Health check and OpenAPI/Swagger at `/docs`

---

## Local Setup

1. Create and activate a virtual environment; from repo root:

   ```bash
   pip install -r backend/requirements.txt
   ```

2. Configure environment (e.g. `backend/.env` or `.env`):

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

3. Run the API:

   ```bash
   uvicorn backend.app.main:app --reload
   ```

4. Open `http://127.0.0.1:8000/docs`.

---

## Testing

Run the full test suite (metrics in “Resume Highlights” come from here):

```bash
pytest backend/tests -q
```

Coverage includes: DB models and relationships, repositories, services, Pydantic schemas, REST endpoints, OAuth flow, and startup/table creation.
