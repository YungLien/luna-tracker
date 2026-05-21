import math
from datetime import date, datetime, timezone, timedelta
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Depends, HTTPException, Query

from app.db.supabase import get_supabase
from app.models.schemas import ActivityResponse
from app.routers.deps import get_current_user
from app.services.strava import get_athlete_activities, get_valid_access_token

MELBOURNE_TZ = ZoneInfo("Australia/Melbourne")

router = APIRouter(prefix="/api/activities", tags=["activities"])


def _strava_display_km(distance_m: float) -> float:
    """Match Strava app: distance is shown rounded down to 0.01 km (10 m)."""
    if not distance_m:
        return 0.0
    return math.floor(distance_m / 10) / 100


def _format_pace(distance_m: float, elapsed_sec: int) -> str | None:
    """Return pace as 'M'SS\" string, e.g. \"5'10\"\"."""
    if not distance_m or not elapsed_sec:
        return None
    pace_sec_per_km = elapsed_sec / (distance_m / 1000)
    mins = int(pace_sec_per_km // 60)
    secs = int(pace_sec_per_km % 60)
    return f"{mins}'{secs:02d}\""


@router.get("/today", response_model=list[ActivityResponse])
async def get_activities_today(user: dict = Depends(get_current_user)):
    """Return today's Strava activities from the database."""
    supabase = get_supabase()
    today = datetime.now(MELBOURNE_TZ).date().isoformat()

    result = (
        supabase.table("activities")
        .select("*")
        .eq("user_id", user["id"])
        .eq("date", today)
        .execute()
    )

    return result.data or []


@router.get("/history", response_model=list[ActivityResponse])
async def get_activities_history(
    days: int = Query(7, ge=1, le=90),
    user: dict = Depends(get_current_user),
):
    """Return activities for the last N days."""
    supabase = get_supabase()
    since = (datetime.now(MELBOURNE_TZ).date() - timedelta(days=days)).isoformat()

    result = (
        supabase.table("activities")
        .select("*")
        .eq("user_id", user["id"])
        .gte("date", since)
        .order("date", desc=True)
        .execute()
    )

    return result.data or []


@router.post("/sync", response_model=list[ActivityResponse])
async def sync_activities(
    days: int = Query(1, ge=1, le=30),
    user: dict = Depends(get_current_user),
):
    """Fetch recent activities from Strava and upsert into the database."""
    supabase = get_supabase()

    access_token = await get_valid_access_token(user, supabase)

    # Use Melbourne midnight so morning runs (e.g. 6 AM AEST = previous UTC day) are included
    now_melb = datetime.now(MELBOURNE_TZ)
    since_melb = (now_melb - timedelta(days=days - 1)).replace(hour=0, minute=0, second=0, microsecond=0)
    after_ts = int(since_melb.astimezone(timezone.utc).timestamp())

    try:
        raw_activities = await get_athlete_activities(access_token, after_ts)
    except Exception:
        raise HTTPException(status_code=502, detail="Failed to fetch from Strava")

    upserted = []

    for act in raw_activities:
        started_at_str = act.get("start_date")
        started_at = datetime.fromisoformat(started_at_str.replace("Z", "+00:00")) if started_at_str else None

        # Convert to Melbourne time so a 6 AM AEST run is stored as today, not yesterday UTC
        if started_at:
            activity_date = started_at.astimezone(MELBOURNE_TZ).date()
        else:
            activity_date = datetime.now(MELBOURNE_TZ).date()

        distance_m = act.get("distance", 0)
        moving_sec = act.get("moving_time") or act.get("elapsed_time", 0)
        distance_km = _strava_display_km(distance_m)
        duration_min = moving_sec  # stored as seconds for H:MM:SS display

        row = {
            "user_id": user["id"],
            "strava_activity_id": act["id"],
            "activity_type": act.get("type", ""),
            "distance_km": distance_km,
            "duration_min": duration_min,
            "pace_per_km": _format_pace(distance_m, moving_sec),
            "started_at": started_at.isoformat() if started_at else None,
            "date": activity_date.isoformat(),
        }

        result = (
            supabase.table("activities")
            .upsert(row, on_conflict="user_id,strava_activity_id")
            .execute()
        )
        if result.data:
            upserted.extend(result.data)

    return upserted
