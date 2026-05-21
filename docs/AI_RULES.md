# AI_RULES.md — Rules for Claude Code

These rules apply to all code generation for the Luna Tracker project.
Read MEMORY.md first to understand the full project context.

---

## Project Identity

- App name: **Luna Tracker**
- Luna is a real black cat. She is the emotional core of this app.
- This is a **personal portfolio project** — code quality and readability matter.
- The developer is building their first React project. Explain new patterns briefly.

---

## General Rules

- Always read the relevant file before editing it
- Never delete existing functionality without asking first
- Keep commits small and focused — one feature per commit
- If something is unclear, ask before writing code
- Prefer simple, readable code over clever one-liners
- Write comments for non-obvious logic (especially Luna state and OAuth flow)

---

## Language & Framework Rules

### Python (Backend)
- Python 3.11+
- Use **FastAPI** with type hints on all route parameters and return types
- Use **Pydantic v2** models for request/response schemas
- Use `async def` for all route handlers
- Environment variables via `python-dotenv` — never hardcode secrets
- Use `httpx` (async) for all HTTP calls to Strava API
- One router file per domain: `auth.py`, `meals.py`, `activities.py`, `dashboard.py`
- All Strava API logic lives in `services/strava.py` — never inline in routers
- Luna state logic lives in `services/luna.py` — pure function, no DB calls

### JavaScript / React (Frontend)
- React 18 with **functional components only** — no class components
- Use **hooks** (useState, useEffect, useCallback) — no Redux, no Zustand
- Use **CSS Modules** for all component styling — no inline styles, no Tailwind
- Use **axios** for all API calls via the shared `api/client.js` instance
- File naming: components in PascalCase (`LunaScene.jsx`), hooks in camelCase (`useLunaState.js`)
- One component per file
- Props should be destructured at the top of each component

---

## Styling Rules

- Mobile-first: design for 390px width first, scale up
- Colour palette: warm pastels — cream (#fdf6ee), soft pink, sage green, warm beige
- No harsh shadows — use soft, warm drop shadows only
- Font: system font stack is fine, or a warm serif/rounded sans if added later
- Minimum tap target size: 44px × 44px for all interactive elements
- Luna images: always `object-fit: contain`, never stretch or crop
- Background scenes: `background-size: cover`, `background-position: center`

---

## Luna Image Rules

Luna pose images live in `src/assets/luna/`. There are 9 files total.

### Filename → Role mapping (do not rename files):

**Layer 1 — Time base poses:**
- `cat_sit_still.png` — Morning base (05:00–10:59)
- `cat_chilling.png` — Afternoon base (11:00–16:59)
- `cat_stretch.png` — Evening base (17:00–19:59)
- `sleepy_cat.png` — Night base (20:00–04:59)

**Layer 2 — Event poses (2-hour duration each):**
- `cat_tickling.png` — Healthy food logged
- `unhappy_cat.png` — Unhealthy food logged
- `playful_cat.png` — Strava run synced

**Layer 3 — Special overrides:**
- `cat_in_shocked.png` — Bubble tea or instant noodles (1 hour, full override)
- `cat_one_leg_up.png` — Streak ≥ 3 days (3-second animation on first open of day)

### Rules:
- Never hardcode pose selection in components — always derive from `useLunaState` hook
- `cat_in_shocked` overrides ALL other poses when active
- `cat_one_leg_up` only plays once per day (on first app open), then drops to Layer 2/1
- Layer 2 priority within events: run > healthy > unhealthy
- After event duration expires, always fall back to current Layer 1 time base pose
- Background scenes live in `src/assets/scenes/`: `morning.png`, `afternoon.png`, `night.png`
- Evening time period (17:00–19:59) reuses `afternoon.png` as background

### Black background handling:
Images were generated with black backgrounds. Use CSS `mix-blend-mode: screen` on the
Luna `<img>` element to blend against the scene background, OR use pre-processed
transparent PNGs if background removal is done beforehand. Do not stretch or crop Luna images.

---

## API Rules

- All `/api/*` routes require a valid JWT in the `Authorization: Bearer` header
- Never return raw Supabase errors to the client — catch and return clean messages
- All dates stored as `DATE` (YYYY-MM-DD) in user's local timezone, not UTC
- Meal uniqueness: one record per (user_id, meal_type, date) — use upsert not insert
- Strava token refresh must happen silently — never expose token errors to the user
- `health_score` (0–10 integer) is the raw user input; `is_healthy` is always derived server-side as a Postgres generated column (`health_score >= 7`). Never accept `is_healthy` as a client-provided field — ignore it if sent.

---

## Security Rules

- Never log access tokens or refresh tokens
- Never commit `.env` files — `.env.example` only
- Supabase service key only used in backend — never expose to frontend
- JWT secret must be at least 32 characters
- CORS: in development allow localhost:5173, in production allow only the Vercel domain

---

## Things NOT to Do

- ❌ Do not add TypeScript — keep it JavaScript for now
- ❌ Do not add Redux, Zustand, or any global state library
- ❌ Do not add Tailwind CSS
- ❌ Do not add a UI component library (shadcn, MUI, etc.)
- ❌ Do not add calorie counting or macro tracking — out of scope
- ❌ Do not add multi-user support — this is single-user only
- ❌ Do not add punishment/negative UI for unhealthy meals — positive only
- ❌ Do not use `any` type in Python without a comment explaining why
- ❌ Do not make more than one Strava API call per user action — batch where possible

---

## Commit Message Format

```
feat: add Strava OAuth callback endpoint
fix: correct token expiry check in refresh logic
style: update LunaScene fade transition timing
docs: add setup instructions to README
```

---

## File to Always Check First

Before making any changes, read `MEMORY.md` to understand the full project context,
design decisions, and current state of the build.
