# Deploy frontend to Vercel (required for phone / production)

The **React app** must be on a public HTTPS URL. Railway only hosts the **API** — opening Railway in Safari shows nothing useful for users.

## Why iPhone showed `localhost:5173/callback`

After Strava login, the backend redirects to `FRONTEND_URL/callback`. If Railway does not have `FRONTEND_URL` set, it defaults to `http://localhost:5173`. On your phone, **localhost = the phone itself**, not your Mac — so the page never loads.

## Vercel setup

1. [vercel.com](https://vercel.com) → **Add New Project** → import `luna-tracker` repo.
2. **Root Directory** → **`frontend`**
3. Framework: **Vite** (auto-detected)
4. **Environment variable** (Production):
   - `VITE_API_BASE_URL` = your Railway URL, e.g. `https://luna-tracker-production.up.railway.app` (no trailing slash)
5. Deploy → note your URL, e.g. `https://luna-tracker.vercel.app`

## Railway variables (after Vercel is live)

Update Railway → **Variables**:

| Variable | Value |
|----------|--------|
| `FRONTEND_URL` | `https://luna-tracker.vercel.app` (your Vercel URL, **no** `/callback`) |
| `ALLOWED_ORIGINS` | Same Vercel URL (comma-separate if you also use localhost for dev) |
| `STRAVA_REDIRECT_URI` | `https://<railway-host>/auth/strava/callback` |

Redeploy Railway after changing variables.

## Strava API settings

Authorization Callback Domain: your Railway host only (e.g. `luna-tracker-production.up.railway.app`).

## Use the app on iPhone

Open **your Vercel URL** in Safari — not `localhost`, not Railway.

Flow: Vercel → Connect Strava → Strava → Railway callback → redirect to `https://your-app.vercel.app/callback?token=...` → Dashboard.

## Local dev (optional)

Keep `FRONTEND_URL=http://localhost:5173` and `VITE_API_BASE_URL=http://localhost:8000` on your machine only — do not use these on Railway for phone testing.
