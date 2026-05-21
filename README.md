# Luna Tracker

A personal health tracker PWA where Luna (a real black cat) reflects your daily habits.
Log meals, sync Strava runs, and watch Luna react.

## Stack

- **Backend:** FastAPI + Supabase Postgres
- **Frontend:** React 18 + Vite (PWA)
- **Auth:** Strava OAuth 2.0

## Setup

### Prerequisites

- Python 3.11+
- Node 18+
- Strava API app credentials
- Supabase project

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # fill in credentials
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
cp .env.example .env   # fill in VITE_API_BASE_URL
npm run dev
```

## Database security (Supabase)

If Security Advisor shows **RLS disabled** on your tables, run the SQL in  
[`supabase/migrations/001_enable_rls.sql`](supabase/migrations/001_enable_rls.sql)  
in the Supabase SQL Editor. See [`supabase/README.md`](supabase/README.md).

## Development

Open `http://localhost:5173` in your browser.  
Backend runs on `http://localhost:8000`.

See `docs/PLAN.md` for the week-by-week build checklist.
