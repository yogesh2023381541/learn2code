# Learn2Code

Learn2Code is a premium technology learning platform. Phase 1 currently includes
the responsive dashboard foundation, subject discovery, progress tracking UI, and
an interactive Python roadmap preview.

## Run locally

```bash
npm install
npm run dev
```

The app is intentionally backed by local mock data in this first slice. The
component boundaries are ready for a REST API and persistent progress service.

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
The API currently provides health checks, signup/login, JWT-protected profile
onboarding, and published subject listing endpoints.