import os
from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import public_config_status
from app.db.supabase import check_supabase_connection
from app.routers import auth, meals, activities, dashboard
from app.services.strava import check_strava_application_credentials

app = FastAPI(title="Luna Tracker API")

_origins_env = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173")
_allowed_origins = [o.strip() for o in _origins_env.split(",")]

app.add_middleware(
    CORSMiddleware,
    allow_origins=_allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(meals.router)
app.include_router(activities.router)
app.include_router(dashboard.router)


@app.get("/health")
def health():
    """Lightweight liveness check for Railway — no external network calls."""
    return {"status": "ok"}


@app.get("/health/diagnostics")
async def health_diagnostics():
    """Full env + Strava/Supabase probes (may be slow; never returns 500)."""
    config = {**public_config_status()}
    try:
        config.update(await check_strava_application_credentials())
    except Exception as exc:
        config["strava_credentials_valid"] = None
        config["strava_credentials_hint"] = f"Strava check crashed: {exc}"[:200]
    try:
        config.update(check_supabase_connection())
    except Exception as exc:
        config["supabase_ok"] = False
        config["supabase_hint"] = f"Supabase check crashed: {exc}"[:200]

    ready = config.get("supabase_ok") is True and config.get("strava_credentials_valid") is True
    return {"status": "ok" if ready else "degraded", "config": config}
