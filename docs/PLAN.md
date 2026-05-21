# PLAN.md — Luna Tracker Build Plan

Read MEMORY.md before starting any week. Update the "Current Build State" checklist
in MEMORY.md as each task is completed.

---

## Week 1 — Foundation: Docs + Environment + Auth

Goal: Strava OAuth works end-to-end. User row created in Supabase. JWT issued.
This is the gate that unlocks everything else — no meal can be logged without a user_id.

### Setup
- [x] Update all docs to reflect Snack category and 0–10 points system
- [x] Register Strava API app at https://www.strava.com/settings/api
      → App name: Luna Tracker, Callback domain: localhost
      → Note Client ID + Client Secret
- [x] Create Supabase project → note Project URL + service role key
- [x] Initialise git repo with .gitignore (node_modules/, __pycache__/, .env, *.pyc, .DS_Store)
- [x] Create minimal README.md

### Database
- [x] Run SQL schema from ARCHITECTURE.md in Supabase SQL editor
- [x] Verify: meals table has 'snack' in CHECK constraint
- [x] Verify: meals.is_healthy is a generated column (health_score >= 7)
- [x] Verify all 4 tables exist: users, meals, activities, daily_summaries

### Backend — Scaffold + OAuth
- [x] Create backend/ folder structure
- [x] Write requirements.txt
- [x] Write backend/.env (from .env.example template)
- [x] Write backend/app/db/supabase.py — Supabase client singleton
- [x] Write backend/app/models/schemas.py — Pydantic v2 models
- [x] Write backend/app/services/strava.py — exchange_code_for_tokens(), refresh_access_token(), get_athlete_activities()
- [x] Write backend/app/routers/auth.py — GET /auth/strava + GET /auth/strava/callback
- [x] Write backend/app/main.py — FastAPI app, CORS, health check, register auth router
- [x] Boot backend: uvicorn app.main:app --reload → confirm GET /health returns 200
- [x] Test full OAuth loop: browser → Strava → callback → user row in Supabase → JWT returned

**Week 1 milestone:** JWT in hand, user row in Supabase. curl /health returns 200. ✓ COMPLETE

---

## Week 2 — Backend: All Routers Live

Goal: Every API endpoint is working and tested with curl. Backend is feature-complete.

- [x] Write backend/app/services/luna.py — get_luna_state() pure function (3-layer system)
- [x] Write backend/app/routers/meals.py
      → POST /api/meals (upsert by user+meal_type+date, body uses health_score not is_healthy)
      → GET /api/meals/today
      → GET /api/meals/history?days=7
- [x] Write backend/app/routers/activities.py
      → GET /api/activities/today
      → POST /api/activities/sync (fetches from Strava, upserts to DB)
- [x] Write backend/app/routers/dashboard.py
      → GET /api/dashboard/today (consolidated: meals + activity + luna state + streak)
- [x] Register all routers in main.py
- [x] Add get_current_user dependency (JWT verification → Supabase user lookup)
- [x] Add silent token refresh in strava.py (check expiry before every Strava API call)
- [x] Test every endpoint with curl using real JWT:
      → POST /api/meals with health_score 8 → is_healthy true in DB ✓
      → GET /api/dashboard/today → snack: null in meals object ✓
      → POST /api/activities/sync → today's run appears ✓

**Week 2 milestone:** curl /api/dashboard/today returns complete, correct JSON. All 4 meal slots present. ✓ COMPLETE

---

## Week 3 — Frontend: Login + Dashboard

Goal: Full app works in browser. User can log in via Strava, see Luna, and log meals.

### Scaffold
- [x] npm create vite@latest frontend -- --template react
- [x] npm install axios react-router-dom
- [x] npm install -D vite-plugin-pwa
- [x] Delete Vite boilerplate (App.css kept but minimal, Vite logo import removed)
- [x] Copy Luna pose images from /image/ → frontend/src/assets/luna/ (9 PNG files present)
- [x] Copy + rename background images:
      morning_bg.png → frontend/src/assets/scenes/morning.png
      afternoon_bg.png → frontend/src/assets/scenes/afternoon.png
      night_bg.png → frontend/src/assets/scenes/night.png
- [x] Write frontend/.env (VITE_API_BASE_URL=http://localhost:8000) + `.env.example`
- [x] Configure vite.config.js (PWA plugin + dev proxy `/auth` + `/api` → backend); Vite pinned to 5.x for Node 20.15

### Auth Flow
- [x] Write frontend/src/api/client.js — axios instance + JWT interceptor
- [x] Write frontend/src/pages/Login.jsx — Strava login button + Luna illustration on sofa
- [x] Write frontend/src/pages/AuthCallback.jsx — reads ?token=, saves to localStorage, redirects to /
- [x] Write frontend/src/App.jsx — React Router (/, /login, /callback)
- [x] Write frontend/src/main.jsx

### Dashboard UI
- [x] Write frontend/src/hooks/useToday.js — timePeriod + scene from current hour
- [x] Write frontend/src/hooks/useLunaState.js — maps pose string → imported PNG
- [x] Write frontend/src/components/LunaScene/LunaScene.jsx + CSS Module
      → mix-blend-mode: multiply on Luna image (white background handling)
- [x] Write frontend/src/components/MealCard/MealCard.jsx + CSS Module
      → logged state: show description + score
      → unlogged state: "Log" button → inline form (text input + 0–10 slider + tag checkboxes)
      → on submit: POST /api/meals → re-fetch dashboard → update state
- [x] Write frontend/src/components/RunCard/RunCard.jsx + CSS Module
- [x] Write frontend/src/components/StreakBadge/StreakBadge.jsx + CSS Module
- [x] Write frontend/src/pages/Dashboard.jsx
      → fetches GET /api/dashboard/today on mount
      → passes data to all components via props (no global state)
      → renders LunaScene + 4x MealCard + RunCard + StreakBadge

### Polish (done alongside Dashboard)
- [x] Login page: Luna positioned on sofa using top:36% with z-index:2
- [x] Login page: real .overlay div (z-index:1) replaces ::after pseudo-element — fixes Luna fading at gradient junction due to mix-blend-mode:multiply interaction
- [x] Dashboard: same 3-layer stacking pattern (scene → Luna z:2 → overlay z:1 → content z:1)

**Week 3 milestone:** App works in browser. Log breakfast score 8 → Luna shows cat_tickling.png. ✓ COMPLETE

---

## Week 4 — PWA + Weekly Summary + Deploy

Goal: App is installable on iPhone. Weekly summary view works. Deployed to Vercel + Railway.

### PWA
- [x] Resize cat_sit_still.png → public/icons/luna-192.png + luna-512.png
      → Padded to 1536×1536 square (cream #FDF6EE bg) before resizing to avoid distortion
- [x] Confirm PWA manifest in vite.config.js (name: 'Luna Tracker', display: standalone)
- [ ] Test "Add to Home Screen" in Safari on iPhone — confirm full screen launch

### Weekly Summary
- [x] Write frontend/src/components/WeeklySheet/WeeklySheet.jsx + CSS Module
      → Bottom sheet (not separate page) with collapsible day cards, insights, weekly km total
- [x] Write frontend/src/pages/Weekly.jsx + Weekly.module.css — standalone full-page fallback
- [x] Add /weekly route to App.jsx
- [x] "This week" button on Dashboard opens WeeklySheet bottom sheet

### Bug Fixes Applied
- [x] first_open_today was hardcoded False → cat_one_leg_up (streak ≥ 3 celebration) never triggered
      → Dashboard.jsx: tracks first open via localStorage key luna_last_open (ISO date)
      → Passes ?first_open=true query param to backend on first daily open
      → dashboard.py: accepts first_open: bool = False query param, passes to get_luna_state()

### Manual QA Checklist
- [x] Log breakfast score 8 → cat_tickling.png (Layer 2 healthy event) ✓
- [x] Log snack with bubble_tea tag → cat_in_shocked.png (Layer 3 override) ✓
- [x] Wait 1 hour → shocked pose clears → returns to time-base pose (code-verified, not manually timed)
- [ ] POST /api/activities/sync with a real run today → playful_cat.png
- [x] 3 consecutive healthy meal days → streak badge shows + cat_one_leg_up on first open ✓
      → 3-second timer implemented in Dashboard.jsx (useEffect watching streak_celebrate)
- [x] Night time → sleepy_cat.png as base pose (tested via ?scene=night) ✓
- [x] App installs and launches correctly on iPhone Safari ✓

### Deployment
- [ ] Push to GitHub
- [ ] Deploy backend to Railway
      → Set all env vars in Railway dashboard
      → Update STRAVA_REDIRECT_URI to Railway URL
- [ ] Deploy frontend to Vercel
      → Set VITE_API_BASE_URL to Railway backend URL
      → Update CORS in backend main.py to allow Vercel domain
- [ ] Re-test full OAuth flow on production URLs
- [ ] Update Strava app callback domain to production domain

**Week 4 milestone:** Live URL. Installable on iPhone. All 5 habit categories working.

---

## Backlog (Post-v1)

Out of scope for v1 but worth noting for future sessions:

- Background removal from Luna PNG images (currently handled with mix-blend-mode: screen)
- Push notifications for meal reminders
- Edit/delete a logged meal (currently only upsert before midnight)
- Apple Health / Google Fit integration
- Strava webhook (real-time activity sync vs. manual refresh)
- Multiple background scenes (currently 3)
