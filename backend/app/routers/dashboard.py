import asyncio
from datetime import date, datetime, timezone, timedelta
from zoneinfo import ZoneInfo

MELBOURNE_TZ = ZoneInfo("Australia/Melbourne")

from fastapi import APIRouter, Depends

from app.db.supabase import get_supabase
from app.models.schemas import (
    ActivitySummary, DashboardResponse, LunaState, MealResponse, UserResponse
)
from app.routers.deps import get_current_user
from app.services.luna import get_luna_state

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


def _compute_streak(supabase, user_id: str) -> int:
    """Count consecutive days where breakfast + lunch + dinner all scored >= 7."""
    streak = 0
    check_date = date.today()

    for _ in range(365):  # cap at 1 year
        day_str = check_date.isoformat()
        result = (
            supabase.table("meals")
            .select("meal_type, is_healthy")
            .eq("user_id", user_id)
            .eq("date", day_str)
            .execute()
        )
        meals_that_day = {m["meal_type"]: m["is_healthy"] for m in (result.data or [])}

        # Streak requires all 3 main meals to be healthy (snack excluded)
        if (
            meals_that_day.get("breakfast") is True
            and meals_that_day.get("lunch") is True
            and meals_that_day.get("dinner") is True
        ):
            streak += 1
            check_date -= timedelta(days=1)
        else:
            break

    return streak


@router.get("/today", response_model=DashboardResponse)
async def get_dashboard_today(first_open: bool = False, user: dict = Depends(get_current_user)):
    supabase = get_supabase()
    now = datetime.now(MELBOURNE_TZ)
    today = now.date().isoformat()

    # Fetch today's meals
    meals_result = await asyncio.to_thread(
        lambda: supabase.table("meals").select("*").eq("user_id", user["id"]).eq("date", today).execute()
    )
    meals_list = meals_result.data or []

    # Fetch today's activities
    activities_result = await asyncio.to_thread(
        lambda: supabase.table("activities").select("*").eq("user_id", user["id"]).eq("date", today).execute()
    )
    activities_list = activities_result.data or []

    # Build meals dict (4 slots, each is None if not yet logged)
    meals_by_type: dict = {"breakfast": None, "lunch": None, "dinner": None, "snack": None}
    for meal in meals_list:
        meals_by_type[meal["meal_type"]] = meal

    # Activity summary
    run_activities = [a for a in activities_list if a.get("activity_type") == "Run"]
    if run_activities:
        best = max(run_activities, key=lambda a: a.get("distance_km", 0))
        activity = ActivitySummary(
            has_run=True,
            distance_km=best.get("distance_km"),
            duration_min=best.get("duration_min"),
            pace=best.get("pace_per_km"),
        )
    else:
        activity = ActivitySummary(has_run=False)

    # Streak
    streak = await asyncio.to_thread(lambda: _compute_streak(supabase, user["id"]))

    luna_data = get_luna_state(
        now=now,
        meals=meals_list,
        activities=activities_list,
        streak=streak,
        first_open_today=first_open,
    )

    return DashboardResponse(
        user=UserResponse(
            id=user["id"],
            name=user.get("name"),
            avatar_url=user.get("avatar_url"),
        ),
        meals=meals_by_type,
        activity=activity,
        luna=LunaState(**luna_data),
        streak=streak,
    )
