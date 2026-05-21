from datetime import datetime, timedelta
from typing import Any


TIME_BASE_POSES: dict[str, str] = {
    "morning":   "cat_sit_still",
    "afternoon": "cat_chilling",
    "evening":   "cat_stretch",
    "night":     "sleepy_cat",
}


def get_time_period(hour: int) -> str:
    if 5 <= hour < 11:  return "morning"
    if 11 <= hour < 17: return "afternoon"
    if 17 <= hour < 20: return "evening"
    return "night"


def _scene(hour: int) -> str:
    if 5 <= hour < 11:  return "morning"
    if 11 <= hour < 20: return "afternoon"  # evening reuses afternoon scene
    return "night"


def get_luna_state(
    now: datetime,
    meals: list[dict[str, Any]],
    activities: list[dict[str, Any]],
    streak: int,
    first_open_today: bool,
) -> dict[str, Any]:
    """
    Pure function — no DB calls. Determines Luna's pose using the 3-layer system:
      Layer 3 (highest): special overrides
      Layer 2 (middle):  event poses (last 2 hours)
      Layer 1 (lowest):  time-based base pose
    """
    hour = now.hour
    two_hours_ago = now - timedelta(hours=2)
    one_hour_ago  = now - timedelta(hours=1)

    def parse_logged_at(meal: dict) -> datetime:
        val = meal.get("logged_at") or meal.get("created_at", "")
        if isinstance(val, str):
            return datetime.fromisoformat(val.replace("Z", "+00:00"))
        return val

    # ── Layer 3: Special overrides ──────────────────────────────────────────

    shocked = any(
        tag in ("bubble_tea", "instant_noodles")
        for meal in meals
        for tag in (meal.get("tags") or [])
        if parse_logged_at(meal) >= one_hour_ago
    )
    if shocked:
        return {"pose": "cat_in_shocked", "layer": 3, "scene": _scene(hour), "streak_celebrate": False}

    streak_celebrate = streak >= 3 and first_open_today
    if streak_celebrate:
        return {"pose": "cat_one_leg_up", "layer": 3, "scene": _scene(hour), "streak_celebrate": True}

    # ── Layer 2: Event poses ────────────────────────────────────────────────

    def act_logged_at(act: dict) -> datetime:
        val = act.get("started_at") or act.get("logged_at") or act.get("created_at")
        if val and isinstance(val, str):
            return datetime.fromisoformat(val.replace("Z", "+00:00"))
        if isinstance(val, datetime):
            return val
        return now - timedelta(hours=25)  # safe fallback — won't trigger event pose

    run_event = any(
        a.get("activity_type") == "Run" and act_logged_at(a) >= two_hours_ago
        for a in activities
    )
    healthy_event = any(
        meal.get("is_healthy") and parse_logged_at(meal) >= two_hours_ago
        for meal in meals
    )
    # Score < 5 (any meal type, including snack) — not only is_healthy (< 7)
    unhealthy_event = any(
        meal.get("health_score", 10) < 5 and parse_logged_at(meal) >= two_hours_ago
        for meal in meals
    )

    # Meal events (2-hour window) take priority over run pose (also 2-hour window)
    if healthy_event:
        return {"pose": "cat_tickling", "layer": 2, "scene": _scene(hour), "streak_celebrate": False}
    if unhealthy_event:
        return {"pose": "unhappy_cat", "layer": 2, "scene": _scene(hour), "streak_celebrate": False}
    if run_event:
        return {"pose": "playful_cat", "layer": 2, "scene": _scene(hour), "streak_celebrate": False}

    # ── Layer 1: Time base pose ─────────────────────────────────────────────
    period = get_time_period(hour)
    return {"pose": TIME_BASE_POSES[period], "layer": 1, "scene": _scene(hour), "streak_celebrate": False}
