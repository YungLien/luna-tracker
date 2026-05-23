# Deploy backend to Railway

## Fix: "Root directory … only found /backend and /frontend"

This repo is a **monorepo**. Railway must build from the **`backend`** folder, not the repo root.

1. Open your **luna-tracker** service on Railway.
2. **Settings** → **Root Directory** → set to **`backend`** (no leading slash).
3. Click **Redeploy** (or push a new commit).

Railway will then see `requirements.txt`, `Procfile`, and `app/main.py`.

## Environment variables

In Railway → **Variables**, add everything from `backend/.env.example`.

**Important:** use `KEY=value` with **no quotes** in the Raw Editor.  
Wrong: `FRONTEND_URL="https://..."` — quotes can prevent the variable from loading.  
Right: `FRONTEND_URL=https://luna-tracker-iota.vercel.app`

| Variable | Example / notes |
|----------|-----------------|
| `STRAVA_CLIENT_ID` | From Strava API app |
| `STRAVA_CLIENT_SECRET` | From Strava API app |
| `STRAVA_REDIRECT_URI` | `https://<your-railway-domain>/auth/strava/callback` |
| `SUPABASE_URL` | Supabase project URL |
| `SUPABASE_SERVICE_KEY` | **service_role** key (not anon) |
| `JWT_SECRET` | `openssl rand -hex 32` |
| `ALLOWED_ORIGINS` | Frontend URL(s), comma-separated, e.g. `https://your-app.vercel.app` |
| `FRONTEND_URL` | Frontend base URL after login redirect, e.g. `https://your-app.vercel.app` (no trailing slash) |

## Strava OAuth

In [Strava API settings](https://www.strava.com/settings/api), set **Authorization Callback Domain** to your Railway host (e.g. `xxx.up.railway.app`) and use the full callback URL above for `STRAVA_REDIRECT_URI`.

## Verify

After deploy: open `https://<your-railway-domain>/health` — should return `{"status":"ok"}`.

## Frontend

Deploy **`frontend/`** to Vercel — see [`docs/DEPLOY_VERCEL.md`](docs/DEPLOY_VERCEL.md).  
Set `VITE_API_BASE_URL` to your Railway URL. Set Railway `FRONTEND_URL` to your Vercel URL.
