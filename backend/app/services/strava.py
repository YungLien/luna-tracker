import os
import time
from datetime import datetime, timezone
from typing import Any

import httpx

STRAVA_TOKEN_URL = "https://www.strava.com/oauth/token"
STRAVA_API_BASE = "https://www.strava.com/api/v3"


async def exchange_code_for_tokens(code: str) -> dict[str, Any]:
    """Exchange OAuth authorization code for access + refresh tokens."""
    async with httpx.AsyncClient() as client:
        resp = await client.post(STRAVA_TOKEN_URL, data={
            "client_id": os.environ["STRAVA_CLIENT_ID"],
            "client_secret": os.environ["STRAVA_CLIENT_SECRET"],
            "code": code,
            "grant_type": "authorization_code",
        })
        resp.raise_for_status()
        return resp.json()


async def refresh_access_token(refresh_token: str) -> dict[str, Any]:
    """Get a fresh access token using the stored refresh token."""
    async with httpx.AsyncClient() as client:
        resp = await client.post(STRAVA_TOKEN_URL, data={
            "client_id": os.environ["STRAVA_CLIENT_ID"],
            "client_secret": os.environ["STRAVA_CLIENT_SECRET"],
            "refresh_token": refresh_token,
            "grant_type": "refresh_token",
        })
        resp.raise_for_status()
        return resp.json()


async def get_valid_access_token(user: dict[str, Any], supabase) -> str:
    """Return a valid access token, refreshing silently if expired."""
    expires_at = user["token_expires_at"]

    # Parse timestamp — Supabase returns ISO string
    if isinstance(expires_at, str):
        exp = datetime.fromisoformat(expires_at.replace("Z", "+00:00"))
    else:
        exp = expires_at

    now = datetime.now(timezone.utc)
    if exp.timestamp() - now.timestamp() < 300:  # refresh if <5 min left
        tokens = await refresh_access_token(user["refresh_token"])
        supabase.table("users").update({
            "access_token": tokens["access_token"],
            "refresh_token": tokens["refresh_token"],
            "token_expires_at": datetime.fromtimestamp(
                tokens["expires_at"], tz=timezone.utc
            ).isoformat(),
        }).eq("id", user["id"]).execute()
        return tokens["access_token"]

    return user["access_token"]


async def get_athlete_activities(access_token: str, after_timestamp: int) -> list[dict[str, Any]]:
    """Fetch activities from Strava that started after the given Unix timestamp."""
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            f"{STRAVA_API_BASE}/athlete/activities",
            headers={"Authorization": f"Bearer {access_token}"},
            params={"after": after_timestamp, "per_page": 30},
        )
        resp.raise_for_status()
        return resp.json()
