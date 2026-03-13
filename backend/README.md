# Backend Setup

This folder contains the FastAPI backend for the Mental Health Tracker project.

## Run Locally

From the repository root:

```bash
pip install -r backend/requirements.txt
uvicorn backend.app.main:app --reload
```

Swagger docs:

```text
http://127.0.0.1:8000/docs
```

## Environment Variables

Required for core startup:

- `DATABASE_URL`
- `JWT_SECRET`
- `JWT_EXPIRES_MINUTES`
- `FRONTEND_URL`

Required for Google OAuth:

- `GOOGLE_CLIENT_ID`
- `GOOGLE_CLIENT_SECRET`
- `GOOGLE_REDIRECT_URI`

Required for journal insights:

- `INSIGHTS_API_KEY`
- `INSIGHTS_MODEL`

## Tests

```bash
pytest backend/tests -q
```
