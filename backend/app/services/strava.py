import hashlib
import time
from datetime import datetime, timezone
from typing import Any

import httpx

from app.config import _env

STRAVA_TOKEN_URL = "https://www.strava.com/oauth/token"
STRAVA_API_BASE = "https://www.strava.com/api/v3"


def _strava_oauth_client_fields() -> dict[str, str]:
    return {
        "client_id": _env("STRAVA_CLIENT_ID"),
        "client_secret": _env("STRAVA_CLIENT_SECRET"),
    }


async def exchange_code_for_tokens(code: str) -> dict[str, Any]:
    """Exchange OAuth authorization code for access + refresh tokens."""
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            STRAVA_TOKEN_URL,
            data={
                **_strava_oauth_client_fields(),
                "code": code,
                "grant_type": "authorization_code",
                # Must match redirect_uri used in /oauth/authorize (Strava requirement).
                "redirect_uri": _env("STRAVA_REDIRECT_URI"),
            },
        )
        resp.raise_for_status()
        return resp.json()


async def refresh_access_token(refresh_token: str) -> dict[str, Any]:
    """Get a fresh access token using the stored refresh token."""
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            STRAVA_TOKEN_URL,
            data={
                **_strava_oauth_client_fields(),
                "refresh_token": refresh_token,
                "grant_type": "refresh_token",
            },
        )
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


async def check_strava_application_credentials() -> dict[str, Any]:
    """
    Probe Strava with a fake code. If app id/secret are wrong, Strava returns
    Application invalid; if they are OK, Strava returns an error about the code instead.
    """
    cid = _env("STRAVA_CLIENT_ID")
    secret = _env("STRAVA_CLIENT_SECRET")
    info: dict[str, Any] = {
        "strava_client_id_set": bool(cid),
        "strava_client_secret_set": bool(secret),
        "strava_client_id": cid,  # not secret — visible in /oauth/authorize URL
        "strava_client_secret_length": len(secret),
        # Compare with local: shasum -a 256 <<<"$STRAVA_CLIENT_SECRET" | cut -c1-12
        "strava_client_secret_fingerprint": hashlib.sha256(secret.encode()).hexdigest()[:12],
    }
    if not cid or not secret:
        info["strava_credentials_valid"] = False
        info["strava_credentials_hint"] = (
            "STRAVA_CLIENT_ID or STRAVA_CLIENT_SECRET is empty in this server environment."
        )
        return info

    try:
        async with httpx.AsyncClient(timeout=8.0) as client:
            resp = await client.post(
                STRAVA_TOKEN_URL,
                data={
                    "client_id": cid,
                    "client_secret": secret,
                    "code": "0" * 40,
                    "grant_type": "authorization_code",
                    "redirect_uri": _env("STRAVA_REDIRECT_URI"),
                },
            )
    except httpx.TimeoutException:
        info["strava_credentials_valid"] = None
        info["strava_credentials_hint"] = "Strava probe timed out (network); credentials not verified."
        return info
    except httpx.HTTPError as exc:
        info["strava_credentials_valid"] = None
        info["strava_credentials_hint"] = f"Strava probe failed: {exc}"[:200]
        return info

    body = resp.text
    body_lower = body.lower()
    if "application" in body_lower and "invalid" in body_lower:
        info["strava_credentials_valid"] = False
        info["strava_credentials_hint"] = (
            "Strava rejected client_id + client_secret. "
            "Re-copy both from https://www.strava.com/settings/api (same app), "
            "paste into Railway without quotes, then redeploy."
        )
    else:
        info["strava_credentials_valid"] = True
        info["strava_credentials_hint"] = (
            "Strava accepted your app credentials (fake code error is expected)."
        )
    return info


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
