# ARCHITECTURE.md — Luna Tracker Technical Architecture

## Tech Stack

| Layer | Technology | Reason |
|---|---|---|
| Frontend | React 18 + Vite | First React project, component-based UI |
| Styling | CSS Modules | Fine-grained control for custom illustrations |
| Charts | Recharts | Simple, composable, React-native charts |
| Backend | FastAPI (Python 3.11+) | Already familiar, fast to build |
| Database | Supabase (Postgres) | Already familiar, handles auth storage |
| Storage | Supabase Storage | Luna pose images if needed |
| Third-party | Strava API v3 | OAuth login + activity data |
| Deployment | Vercel (frontend) + Railway (backend) | Free tier, portfolio-ready |
| PWA | Vite PWA Plugin | iPhone "Add to Home Screen" support |

---

## Repository Structure

```
luna_tracker/
├── frontend/
│   ├── public/
│   │   ├── icons/              # PWA icons (Luna avatar)
│   │   └── manifest.json
│   ├── src/
│   │   ├── assets/
│   │   │   ├── luna/           # Luna pose PNGs (transparent bg)
│   │   │   │   ├── waiting.png
│   │   │   │   ├── sunny.png
│   │   │   │   ├── blanket.png
│   │   │   │   ├── sleeping.png
│   │   │   │   ├── cheering.png
│   │   │   │   ├── tv.png
│   │   │   │   ├── crown.png
│   │   │   │   └── shy.png
│   │   │   └── scenes/         # Background scene PNGs
│   │   │       ├── morning.png
│   │   │       ├── afternoon.png
│   │   │       └── night.png
│   │   ├── components/
│   │   │   ├── LunaScene/      # Main illustration display
│   │   │   ├── MealCard/       # Meal logging card per slot
│   │   │   ├── RunCard/        # Strava activity display
│   │   │   ├── StreakBadge/    # Consecutive day counter
│   │   │   └── WeeklySummary/  # Recharts weekly view
│   │   ├── hooks/
│   │   │   ├── useLunaState.js # Determines pose from meal + time
│   │   │   └── useToday.js     # Current time period logic
│   │   ├── pages/
│   │   │   ├── Login.jsx       # Strava OAuth entry point
│   │   │   ├── Dashboard.jsx   # Main daily view
│   │   │   └── Weekly.jsx      # Weekly summary
│   │   ├── api/
│   │   │   └── client.js       # Axios instance with base URL + auth header
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── vite.config.js
│   └── package.json
│
├── backend/
│   ├── app/
│   │   ├── main.py             # FastAPI app entry
│   │   ├── routers/
│   │   │   ├── auth.py         # Strava OAuth endpoints
│   │   │   ├── meals.py        # Meal CRUD
│   │   │   ├── activities.py   # Strava sync + retrieval
│   │   │   └── dashboard.py    # Today's summary endpoint
│   │   ├── services/
│   │   │   ├── strava.py       # Strava API client + token refresh
│   │   │   └── luna.py         # Luna state calculation logic
│   │   ├── models/
│   │   │   └── schemas.py      # Pydantic models
│   │   └── db/
│   │       └── supabase.py     # Supabase client setup
│   ├── .env
│   └── requirements.txt
│
├── docs/
│   ├── PRD.md
│   ├── ARCHITECTURE.md
│   ├── PLAN.md
│   ├── AI_RULES.md
│   └── MEMORY.md
│
└── README.md
```

---

## Database Schema (Supabase Postgres)

```sql
-- Users (one record per person, keyed to Strava)
CREATE TABLE users (
  id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  strava_id     BIGINT UNIQUE NOT NULL,
  name          TEXT,
  avatar_url    TEXT,
  access_token  TEXT NOT NULL,
  refresh_token TEXT NOT NULL,
  token_expires_at TIMESTAMPTZ NOT NULL,
  created_at    TIMESTAMPTZ DEFAULT now()
);

-- Meals (one record per meal slot per day)
CREATE TABLE meals (
  id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id      UUID REFERENCES users(id) ON DELETE CASCADE,
  meal_type    TEXT NOT NULL CHECK (meal_type IN ('breakfast', 'lunch', 'dinner', 'snack')),
  description  TEXT NOT NULL,
  health_score SMALLINT NOT NULL CHECK (health_score BETWEEN 0 AND 10),
  is_healthy   BOOLEAN GENERATED ALWAYS AS (health_score >= 7) STORED,
  tags         TEXT[],           -- e.g. ['bubble_tea'], ['instant_noodles']
  logged_at    TIMESTAMPTZ DEFAULT now(),
  date         DATE NOT NULL,    -- local date (YYYY-MM-DD)
  UNIQUE (user_id, meal_type, date)
);

-- Activities (synced from Strava)
CREATE TABLE activities (
  id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id             UUID REFERENCES users(id) ON DELETE CASCADE,
  strava_activity_id  BIGINT UNIQUE NOT NULL,
  activity_type       TEXT,          -- 'Run', 'Ride', etc.
  distance_km         NUMERIC(6,2),
  duration_min        INTEGER,
  pace_per_km         TEXT,          -- formatted string e.g. "5'10\""
  started_at          TIMESTAMPTZ,
  date                DATE NOT NULL,
  UNIQUE (user_id, strava_activity_id)
);

-- Daily summaries (computed, cached for streak calculation)
-- streak_days counts only days where breakfast_ok + lunch_ok + dinner_ok are all TRUE
-- snack_ok is tracked separately and does not affect streak
CREATE TABLE daily_summaries (
  id             UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id        UUID REFERENCES users(id) ON DELETE CASCADE,
  date           DATE NOT NULL,
  breakfast_ok   BOOLEAN DEFAULT FALSE,
  lunch_ok       BOOLEAN DEFAULT FALSE,
  dinner_ok      BOOLEAN DEFAULT FALSE,
  snack_ok       BOOLEAN DEFAULT FALSE,
  has_activity   BOOLEAN DEFAULT FALSE,
  streak_days    INTEGER DEFAULT 0,
  UNIQUE (user_id, date)
);
```

**Row Level Security:** After creating tables, run `supabase/migrations/001_enable_rls.sql` in the Supabase SQL Editor. All tables have RLS enabled with no public policies; only the backend `service_role` key (via FastAPI) can access data.

---

## API Design

### Auth

```
GET  /auth/strava
     → Redirects user to Strava OAuth consent page

GET  /auth/strava/callback?code=xxx
     → Exchanges code for tokens
     → Upserts user in DB
     → Returns session token (JWT or cookie)

POST /auth/logout
     → Clears session
```

### Meals

```
GET  /api/meals/today
     → Returns all meal records for today (user scoped)

POST /api/meals
     Body: { meal_type, description, health_score, tags[] }
     → Creates or updates meal for that slot today
     → is_healthy is derived server-side (health_score >= 7), never client-provided

GET  /api/meals/history?days=7
     → Returns last N days of meal records
```

### Activities

```
GET  /api/activities/today
     → Returns today's Strava activities (from DB)

POST /api/activities/sync
     → Fetches latest from Strava API, upserts into DB
     → Called on login + manual refresh
```

### Dashboard

```
GET  /api/dashboard/today
     → Returns single consolidated response:
        {
          user: { name, avatar_url },
          meals: { breakfast, lunch, dinner, snack },
          activity: { has_run, distance_km, duration_min, pace },
          luna: { pose, scene, crown, shy },
          streak: 5
        }
     → Each meal entry shape: { description, health_score, is_healthy, tags }
     → Snack does not contribute to streak calculation
```

---

## Luna State Logic (backend service)

```python
# services/luna.py
# 3-layer priority system: Special > Event > Time Base

from datetime import datetime, timedelta

def get_time_period(hour: int) -> str:
    if 5 <= hour < 11:  return 'morning'
    if 11 <= hour < 17: return 'afternoon'
    if 17 <= hour < 20: return 'evening'
    return 'night'

TIME_BASE_POSES = {
    'morning':   'cat_sit_still',   # Sitting up, waiting
    'afternoon': 'cat_chilling',    # Lying flat, lazy
    'evening':   'cat_stretch',     # Stretching, hinting movement
    'night':     'sleepy_cat',      # Curled up asleep
}

def get_luna_state(now: datetime, meals: list, activities: list,
                   streak: int, first_open_today: bool) -> dict:

    hour = now.hour
    two_hours_ago = now - timedelta(hours=2)
    one_hour_ago  = now - timedelta(hours=1)

    # --- Layer 3: Special overrides (highest priority) ---

    # Streak celebration: only on first app open of day, shows for 3 seconds
    streak_celebrate = streak >= 3 and first_open_today

    # Shocked: bubble tea or instant noodles logged within last hour
    shocked = any(
        tag in ('bubble_tea', 'instant_noodles')
        for meal in meals
        for tag in (meal.tags or [])
        if meal.logged_at >= one_hour_ago
    )

    if shocked:
        return { 'pose': 'cat_in_shocked', 'layer': 3,
                 'scene': _scene(hour), 'streak_celebrate': False }

    if streak_celebrate:
        return { 'pose': 'cat_one_leg_up', 'layer': 3,
                 'scene': _scene(hour), 'streak_celebrate': True }

    # --- Layer 2: Event poses (last 2 hours each) ---

    # Run event: any Strava activity logged today within last 2 hours
    run_event = any(a.logged_at >= two_hours_ago for a in activities)

    # Healthy food event: any healthy meal logged within last 2 hours
    healthy_event = any(
        m.is_healthy and m.logged_at >= two_hours_ago for m in meals
    )

    # Unhealthy food event: any unhealthy meal (non-special-tag) within last 2 hours
    unhealthy_event = any(
        not m.is_healthy and m.logged_at >= two_hours_ago for m in meals
    )

    # Priority within Layer 2: run > healthy > unhealthy
    if run_event:
        return { 'pose': 'playful_cat', 'layer': 2,
                 'scene': _scene(hour), 'streak_celebrate': False }
    if healthy_event:
        return { 'pose': 'cat_tickling', 'layer': 2,
                 'scene': _scene(hour), 'streak_celebrate': False }
    if unhealthy_event:
        return { 'pose': 'unhappy_cat', 'layer': 2,
                 'scene': _scene(hour), 'streak_celebrate': False }

    # --- Layer 1: Time base pose (fallback) ---
    period = get_time_period(hour)
    return { 'pose': TIME_BASE_POSES[period], 'layer': 1,
             'scene': _scene(hour), 'streak_celebrate': False }

def _scene(hour: int) -> str:
    if 5 <= hour < 11:  return 'morning'
    if 11 <= hour < 20: return 'afternoon'  # evening reuses afternoon scene
    return 'night'
```

---

## Time Period Logic (frontend)

```javascript
// hooks/useToday.js
function getTimePeriod() {
  const hour = new Date().getHours()
  if (hour >= 5  && hour < 11) return 'morning'
  if (hour >= 11 && hour < 17) return 'afternoon'
  if (hour >= 17 && hour < 20) return 'evening'
  return 'night'
}
```

---

## OAuth 2.0 Flow (Strava)

```
1. User hits GET /auth/strava
2. Backend redirects to:
   https://www.strava.com/oauth/authorize
     ?client_id=YOUR_ID
     &redirect_uri=YOUR_CALLBACK_URL
     &response_type=code
     &scope=activity:read_all

3. User approves on Strava

4. Strava redirects to GET /auth/strava/callback?code=xxx

5. Backend POSTs to https://www.strava.com/oauth/token
   with { client_id, client_secret, code, grant_type: authorization_code }

6. Strava returns { access_token, refresh_token, expires_at, athlete }

7. Backend upserts user + tokens in Supabase, returns session to frontend

8. On each API call, backend checks token expiry
   → if expired: POST to /oauth/token with grant_type=refresh_token
   → update DB with new tokens
```

---

## PWA Configuration

```javascript
// vite.config.js (VitePWA plugin)
VitePWA({
  registerType: 'autoUpdate',
  manifest: {
    name: 'Luna Tracker',
    short_name: 'Luna',
    theme_color: '#fdf6ee',
    background_color: '#fdf6ee',
    display: 'standalone',        // full screen, no browser chrome
    orientation: 'portrait',
    icons: [
      { src: '/icons/luna-192.png', sizes: '192x192', type: 'image/png' },
      { src: '/icons/luna-512.png', sizes: '512x512', type: 'image/png' }
    ]
  }
})
```

---

## Environment Variables

```
# backend/.env
STRAVA_CLIENT_ID=
STRAVA_CLIENT_SECRET=
STRAVA_REDIRECT_URI=http://localhost:8000/auth/strava/callback
SUPABASE_URL=
SUPABASE_SERVICE_KEY=
JWT_SECRET=

# frontend/.env
VITE_API_BASE_URL=http://localhost:8000
```
