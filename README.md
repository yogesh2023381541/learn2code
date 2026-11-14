# Learn2Code

Learn2Code is a premium technology learning platform. Phase 1 currently includes
the responsive dashboard foundation, subject discovery, progress tracking UI, and
an interactive Python roadmap preview.

## Run locally

```bash
npm install
npm run dev
```

The dashboard requires an authenticated API session. Subjects remain available
from the public API, while dashboard metrics and onboarding are loaded from the
authenticated PostgreSQL-backed service.

## API foundation

The FastAPI service lives in [`backend/`](./backend). Start PostgreSQL, install
the Python dependencies, and run:

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Set the values in `backend/.env.example` in your environment before deploying.
Apply the schema and seed catalog before starting the API:

```bash
alembic upgrade head
uvicorn app.main:app --reload --port 8000
```

The API provides access and rotating refresh JWTs, secure password hashing,
logout/revocation, authenticated profile/onboarding, dashboard metrics, a
persisted lesson library and progress tracking, practice problems/submissions,
bookmarks, history, and profile settings. Learning activity is persisted and
powers the dashboard chart and daily goal. Apply the latest migration before
starting the API. Run backend tests with:

```bash
python -m pytest -q
```

## Run the complete container stack

Set a production-strength secret, then start PostgreSQL, the migrated API, and
the Nginx-served frontend:

```bash
export JWT_SECRET="$(openssl rand -hex 32)"
docker-compose up --build
```

The frontend is available at `http://localhost:5173` and the API at
`http://localhost:8000`.