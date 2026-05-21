# MEMORY.md — Luna Tracker Project Context

This file is the single source of truth for any new Claude session working on
Luna Tracker. Read this entire file before writing any code or making suggestions.

---

## Current Build State

- [x] Docs updated for Snack + points system
- [x] Git repo initialised + .gitignore added
- [x] Strava API app registered (Client ID + Secret obtained)
- [x] Supabase project created (URL + service key obtained)
- [x] Supabase tables created (users, meals, activities, daily_summaries) — per PLAN; re-verify in SQL Editor if needed
- [x] Backend: all files written (main.py, routers, services, models, db)
- [x] Backend: FastAPI app boots (`GET /health` returns 200)
- [x] Backend: Strava OAuth working end-to-end
- [x] Backend: JWT issued + user row created in Supabase
- [x] Backend: All routers live (meals, activities, dashboard)
- [x] Frontend: React + Vite scaffold created (axios, react-router-dom, vite-plugin-pwa, dev proxy, `.env.example`)
- [x] Frontend: Login page — Luna on sofa, Strava connect button
- [x] Frontend: AuthCallback stores JWT, redirects to Dashboard
- [x] Frontend: Dashboard renders with real API data
- [x] Frontend: Meal logging form works (all 4 slots)
- [x] Frontend: Luna pose updates on meal log
- [x] Bug fix: Luna z-index raised above meal card edit forms (content z-index 3)
- [x] Bug fix: Night scene not showing — backend now uses Melbourne timezone (ZoneInfo) instead of UTC
- [x] Bug fix: Bubble tea / noodles checkboxes removed; backend auto-detects tags from description text
- [x] Luna position tuned per scene: night scene sofa (top: 32%, left: 67%)
- [x] Greeting text-shadow added for readability over scene backgrounds
- [x] PWA icons: luna-192.png + luna-512.png created (padded to square, cream bg)
- [x] PWA manifest confirmed in vite.config.js
- [x] WeeklySheet bottom sheet component (Dashboard "This week" button)
- [x] Weekly.jsx standalone page + /weekly route in App.jsx
- [x] Bug fix: first_open_today hardcoded False → now tracked via localStorage luna_last_open
- [ ] Manual QA: 7 items (meal pose, bubble tea, streak, run, night, iPhone install)
- [ ] Deployed to Vercel + Railway (Week 4)

---

## What Is This Project

**Luna Tracker** is a personal health tracker PWA built by the developer for
themselves. It features Luna — their real black cat — as a digital companion
whose mood and activities reflect the developer's daily eating and exercise habits.

This is a **portfolio project** demonstrating:
- OAuth 2.0 third-party API integration (Strava)
- React (developer's first React project)
- FastAPI backend with relational database design
- PWA (installable on iPhone via Safari)
- Personal, story-driven product thinking

---

## The Developer's Context

- Based in Melbourne, Australia
- Background: Software Developer with experience in Python, REST APIs, Supabase,
  Vanilla JS/HTML/CSS, FastAPI
- Previous projects: `photo_organizer` (FastAPI + duplicate detection pipeline),
  `discman` (Supabase + Web Audio API voice postcard app)
- Currently training for a marathon, uses Strava to track runs
- Wants to improve diet — known weak spots: bubble tea, instant noodles, skipping breakfast
- This is their **first React project**

---

## Luna — The Cat

- Luna is the developer's real black cat
- She is a small, fluffy black cat with big golden/yellow eyes
- Her digital version in this app is a **handdrawn pastel illustration**
  in a warm, cozy indoor aesthetic (think: Korean/Japanese indie illustration style)
- She is the emotional core of the app — all design decisions serve her character

---

## Luna Pose System

All poses are real AI-generated PNG files with **white/cream backgrounds** (not transparent, not black).
Stored in `src/assets/luna/`. 9 files exist; not all are used — do not force unused ones in.

| Filename | Visual Description |
|---|---|
| `cat_sit_still.png` | Sitting upright, big golden eyes looking directly at you, calm and attentive |
| `cat_chilling.png` | Lying flat, chin on ground, eyes open and relaxed, totally unbothered |
| `unhappy_cat.png` | Back turned, facing away, tail curled — you cannot see her face |
| `playful_cat.png` | Front paws down, bottom raised, tail up, mouth open — ready to pounce |
| `sleepy_cat.png` | Curled into a tight ball, eyes fully closed, deeply asleep |
| `cat_in_shocked.png` | Arched back, fur puffed up, wide eyes, mouth open — dramatically startled |
| `cat_tickling.png` | Sitting, one paw raised to cheek, eyes squinted in a happy smile |
| `cat_stretch.png` | Front paws stretched forward low, bottom raised high, tail up — big stretch |
| `cat_sit_still.png` | (also used as night neutral — same file, different context) |

**Unused file:** none — all 9 are assigned below.

---

## Luna State System — Layered Architecture

Luna's pose is determined by a **3-layer priority system**:

```
Layer 3 (highest): Special override poses — trump everything
Layer 2 (middle):  Event-triggered poses — triggered by logging, last 2 hours
Layer 1 (lowest):  Time-based base poses — always running in background
```

### Layer 1 — Time Base Poses (default when no event active)

| Time Period | Hours | Pose File | Vibe |
|---|---|---|---|
| Morning | 05:00–10:59 | `cat_sit_still.png` | Sitting up, waiting for you to eat breakfast |
| Afternoon | 11:00–16:59 | `cat_chilling.png` | Lying flat, lazy afternoon |
| Evening | 17:00–19:59 | `cat_stretch.png` | Stretching, hinting you should move too |
| Night | 20:00–04:59 | `sleepy_cat.png` | Curled up asleep, quiet night |

### Layer 2 — Event Poses (triggered by user action, last 2 hours each)

| Event | Pose File | Duration | Notes |
|---|---|---|---|
| Logged healthy food | `cat_tickling.png` | 2 hours | Happy paw-to-cheek smile |
| Logged unhealthy food | `unhappy_cat.png` | 2 hours | Back turned — not angry, just unimpressed |
| Strava run synced today | `playful_cat.png` | 2 hours | Pounce pose — celebrating your run |

**Important:** Event poses override the time base pose for their duration, then
the display returns to the current Layer 1 base pose automatically.

### Layer 3 — Special Poses (highest priority, override everything)

| Trigger | Pose File | Duration | Behaviour |
|---|---|---|---|
| Bubble tea or instant noodles tag logged | `cat_in_shocked.png` | 1 hour | Full override — dramatic, funny, not punishing |
| Streak ≥ 3 consecutive healthy days | `cat_one_leg_up.png` | First open of day only | Plays for 3 seconds on app open, then drops to Layer 2/1 |

**Priority order in code:**
```
if shocked_event_active:        → cat_in_shocked.png
elif streak_celebration_active: → cat_one_leg_up.png  (3s animation on open)
elif run_event_active:          → playful_cat.png
elif healthy_food_event_active: → cat_tickling.png
elif unhealthy_food_event_active: → unhappy_cat.png
else:                           → time-based base pose
```

---

## Background Scenes (3 scenes)

Stored in `src/assets/scenes/`. These are full-bleed background images.

| Filename | Time Period | Hours | Mood |
|---|---|---|---|
| `morning.png` | Morning | 05:00–10:59 | Window with curtains, morning light, cream/yellow tones |
| `afternoon.png` | Afternoon + Evening | 11:00–19:59 | Living room carpet, warm afternoon light, sage/terracotta |
| `night.png` | Night | 20:00–04:59 | Pink sofa, warm lamp, dark window, pink/navy tones |

Evening (17:00–19:59) reuses `afternoon.png` — 3 backgrounds is sufficient.

---

## Design Decisions Made (and why)

| Decision | Rationale |
|---|---|
| No punishment for unhealthy meals | Developer explicitly requested positive-only reinforcement |
| Streak resets silently | No negative UI — just returns to normal Luna state |
| Running not tied to a time period | Developer runs at variable times (morning/afternoon/evening); Strava tracks it |
| Single user app | Personal tool, no need for multi-user complexity |
| PWA not native app | Portfolio use case — no need for App Store; iPhone install via Safari |
| 3-layer pose system | Time base + event override + special override — clean separation of concerns |
| Event poses last 2 hours (all events) | Consistent duration for all Layer 2 events including runs — simple and predictable |
| cat_in_shocked for bubble tea/noodles | More fun and characterful than "shy" — dramatic reaction, not punishment |
| Streak celebration is 3-second animation on open | Non-intrusive, celebratory, doesn't block UI |
| Evening scene reuses afternoon.png | Simplification — 3 backgrounds is sufficient |
| Special tags: bubble_tea, instant_noodles | Developer's specific real-life habits, makes the app feel personal |
| Tag auto-detection in backend (meals.py) | No checkboxes in UI — backend reads description text and sets tags automatically. Matches: "bubble tea", "bubble milk tea", "milk tea", "boba" → bubble_tea; "instant noodle/noodles" → instant_noodles |
| Backend uses ZoneInfo("Australia/Melbourne") for luna state | Timezone was UTC which caused wrong scene/pose at night. Fixed in dashboard.py |
| Luna position: top 32%, left 67% | Tuned for night scene sofa. May need per-scene offsets if morning/afternoon scenes look off |
| Image assets have white/cream backgrounds | AI-generated images came with white BG — handle with CSS `mix-blend-mode: multiply` (makes white transparent, keeps dark pixels) |
| 5 habit categories: Breakfast, Lunch, Dinner, Snack, Run | User confirmed; Snack has no fixed time and is purely optional |
| Health score 0–10 replaces binary healthy/unhealthy | More nuanced; user enters score manually in v1 (no AI parsing) |
| `is_healthy` is a Postgres generated column (`health_score >= 7`) | Single source of truth; changing the threshold only requires one DB change |
| Snack excluded from streak calculation | Streak = Breakfast + Lunch + Dinner all scoring ≥ 7; skipping Snack does not break streak |

---

## Tech Stack (confirmed)

```
Frontend:   React 18 + Vite
Styling:    CSS Modules
Charts:     Recharts
Backend:    FastAPI (Python 3.11+)
Database:   Supabase Postgres
Storage:    Supabase Storage (for images if needed)
Auth:       Strava OAuth 2.0 → JWT session
Deploy:     Vercel (frontend) + Railway (backend)
PWA:        vite-plugin-pwa
```

---

## API — Key Endpoints

```
GET  /auth/strava                   → Redirect to Strava OAuth
GET  /auth/strava/callback          → Handle OAuth callback, return JWT
POST /auth/logout                   → Clear session

GET  /api/dashboard/today           → Single consolidated endpoint (main screen)
POST /api/meals                     → Log/update a meal
GET  /api/meals/today               → Today's meals
GET  /api/meals/history?days=7      → Weekly history
GET  /api/activities/today          → Today's Strava activities
POST /api/activities/sync           → Pull fresh data from Strava API
```

### Dashboard response shape:
```json
{
  "user": { "name": "...", "avatar_url": "..." },
  "meals": {
    "breakfast": { "description": "燕麥", "health_score": 9, "is_healthy": true, "tags": [] },
    "lunch": null,
    "dinner": null,
    "snack": null
  },
  "activity": {
    "has_run": true,
    "distance_km": 8.2,
    "duration_min": 42,
    "pace": "5'10\""
  },
  "luna": {
    "pose": "sunny",
    "scene": "morning",
    "crown": false,
    "shy": false
  },
  "streak": 3
}
```

---

## Database Tables (Supabase Postgres)

```
users           — strava_id, tokens, name, avatar_url
meals           — user_id, meal_type, description, is_healthy, tags[], date
activities      — user_id, strava_activity_id, type, distance_km, duration_min, date
daily_summaries — user_id, date, breakfast_ok, lunch_ok, dinner_ok, has_activity, streak_days
```

Full schema with SQL is in `ARCHITECTURE.md`.

---

## Image Assets — Status

Luna pose images have been **generated and confirmed**. 9 PNG files exist with black backgrounds.

| File | Assigned To |
|---|---|
| `cat_sit_still.png` | Layer 1: Morning base |
| `cat_chilling.png` | Layer 1: Afternoon base |
| `cat_stretch.png` | Layer 1: Evening base |
| `sleepy_cat.png` | Layer 1: Night base |
| `cat_tickling.png` | Layer 2: Healthy food event |
| `unhappy_cat.png` | Layer 2: Unhealthy food event |
| `playful_cat.png` | Layer 2: Run event |
| `cat_in_shocked.png` | Layer 3: Bubble tea / instant noodles override |
| `cat_one_leg_up.png` | Layer 3: Streak ≥ 3 celebration |

**Note on white backgrounds:** Images were AI-generated with white/cream backgrounds, not
transparent. Handle in CSS with `mix-blend-mode: multiply` on the Luna image element —
this makes the white background disappear while keeping Luna's dark pixels visible.
Do NOT use `mix-blend-mode: screen` (that's for black backgrounds).

---

## What Remains (Week 4)

Most of Week 4 is complete. The app is fully functional locally. Remaining work:

1. **Manual QA** — 7 browser/device tests (see PLAN.md QA checklist)
2. **iPhone install test** — Safari "Add to Home Screen", confirm full-screen launch with Luna icon
3. **Deploy** — Railway (backend) + Vercel (frontend), update Strava callback domain, update CORS

See PLAN.md Week 4 for task breakdown.

### WeeklySheet implementation note
Weekly summary was built as a **bottom sheet** (`WeeklySheet.jsx`) launched from a "This week" button on the Dashboard, rather than a separate page. A standalone `Weekly.jsx` page with `/weekly` route also exists. No Recharts — uses plain CSS layout with collapsible day cards and auto-generated insights.

---

## CSS Stacking Pattern (Login + Dashboard share this)

Three-layer z-index system used on both pages:
```
Background scene image (CSS background-image on .page)
  └─ Luna img         z-index: 2  (mix-blend-mode: multiply)
  └─ .overlay div     z-index: 1  (gradient from bottom, pointer-events: none)
  └─ .content div     z-index: 1  (cards and UI)
```
Use a **real div** for the overlay, never `::after` pseudo-element — pseudo-elements paint
after all children in DOM order and would layer over Luna, causing her to fade with multiply.

---

## Files to Read Before Starting

1. `MEMORY.md` (this file)
2. `AI_RULES.md` — coding conventions and constraints
3. `ARCHITECTURE.md` — full technical spec
4. `PRD.md` — product requirements
5. `PLAN.md` — week-by-week task list

Next focus: **Week 4** — PWA, WeeklySummary, deploy.
