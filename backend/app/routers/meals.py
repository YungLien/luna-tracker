from datetime import date, datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query

from app.db.supabase import get_supabase
from app.models.schemas import MealCreate, MealResponse
from app.routers.deps import get_current_user

router = APIRouter(prefix="/api/meals", tags=["meals"])


def _auto_tags(description: str) -> list[str]:
    desc = description.lower()
    tags = []
    if any(kw in desc for kw in ("bubble tea", "bubble milk tea", "milk tea", "boba")):
        tags.append("bubble_tea")
    if any(kw in desc for kw in ("instant noodle", "instant noodles")):
        tags.append("instant_noodles")
    return tags


@router.post("", response_model=MealResponse)
async def log_meal(body: MealCreate, user: dict = Depends(get_current_user)):
    """Create or update a meal for today. One row per (user, meal_type, date)."""
    supabase = get_supabase()
    today = date.today().isoformat()

    data = {
        "user_id": user["id"],
        "meal_type": body.meal_type,
        "description": body.description,
        "health_score": body.health_score,
        "tags": _auto_tags(body.description),
        "date": today,
        "logged_at": datetime.now(timezone.utc).isoformat(),
    }

    result = (
        supabase.table("meals")
        .upsert(data, on_conflict="user_id,meal_type,date")
        .execute()
    )

    if not result.data:
        raise HTTPException(status_code=500, detail="Failed to save meal")

    return result.data[0]


@router.delete("/{meal_id}", status_code=204)
async def delete_meal(meal_id: str, user: dict = Depends(get_current_user)):
    """Delete a meal by ID (only if it belongs to the current user)."""
    supabase = get_supabase()
    supabase.table("meals").delete().eq("id", meal_id).eq("user_id", user["id"]).execute()


@router.get("/today", response_model=list[MealResponse])
async def get_meals_today(user: dict = Depends(get_current_user)):
    """Return all meal records for today."""
    supabase = get_supabase()
    today = date.today().isoformat()

    result = (
        supabase.table("meals")
        .select("*")
        .eq("user_id", user["id"])
        .eq("date", today)
        .execute()
    )

    return result.data or []


@router.get("/history", response_model=list[MealResponse])
async def get_meal_history(
    days: int = Query(7, ge=1, le=90),
    user: dict = Depends(get_current_user),
):
    """Return meals for the last N days."""
    supabase = get_supabase()
    from datetime import timedelta
    since = (date.today() - timedelta(days=days)).isoformat()

    result = (
        supabase.table("meals")
        .select("*")
        .eq("user_id", user["id"])
        .gte("date", since)
        .order("date", desc=True)
        .execute()
    )

    return result.data or []
