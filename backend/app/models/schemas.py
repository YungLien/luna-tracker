from __future__ import annotations
from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, field_validator


# ── Meals ──────────────────────────────────────────────────────────────────

class MealCreate(BaseModel):
    meal_type: str  # breakfast | lunch | dinner | snack
    description: str
    health_score: int  # 0–10; is_healthy derived server-side
    tags: list[str] = []

    @field_validator("meal_type")
    @classmethod
    def validate_meal_type(cls, v: str) -> str:
        allowed = {"breakfast", "lunch", "dinner", "snack"}
        if v not in allowed:
            raise ValueError(f"meal_type must be one of {allowed}")
        return v

    @field_validator("health_score")
    @classmethod
    def validate_health_score(cls, v: int) -> int:
        if not 0 <= v <= 10:
            raise ValueError("health_score must be between 0 and 10")
        return v


class MealResponse(BaseModel):
    id: str
    meal_type: str
    description: str
    health_score: int
    is_healthy: bool
    tags: list[str]
    logged_at: datetime
    date: date


# ── Activities ─────────────────────────────────────────────────────────────

class ActivityResponse(BaseModel):
    id: str
    strava_activity_id: int
    activity_type: str
    distance_km: float
    duration_min: int
    pace_per_km: Optional[str]
    started_at: Optional[datetime]
    date: date


# ── User ───────────────────────────────────────────────────────────────────

class UserResponse(BaseModel):
    id: str
    name: Optional[str]
    avatar_url: Optional[str]


# ── Dashboard ──────────────────────────────────────────────────────────────

class ActivitySummary(BaseModel):
    has_run: bool
    distance_km: Optional[float] = None
    duration_min: Optional[int] = None
    pace: Optional[str] = None


class LunaState(BaseModel):
    pose: str
    scene: str
    layer: int
    streak_celebrate: bool


class DashboardResponse(BaseModel):
    user: UserResponse
    meals: dict[str, Optional[MealResponse]]  # breakfast/lunch/dinner/snack → meal or None
    activity: ActivitySummary
    luna: LunaState
    streak: int
