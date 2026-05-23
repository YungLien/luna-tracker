from datetime import datetime, timedelta, timezone

import httpx
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import RedirectResponse
from jose import jwt

from app.config import _env, frontend_base_url
from app.db.supabase import get_supabase
from app.services.strava import exchange_code_for_tokens

router = APIRouter(prefix="/auth", tags=["auth"])



def _create_jwt(user_id: str) -> str:
    secret = _env("JWT_SECRET")
    if not secret:
        raise HTTPException(status_code=500, detail="JWT_SECRET is not set on the server")
    payload = {
        "sub": user_id,
        "exp": datetime.now(timezone.utc) + timedelta(days=30),
    }
    return jwt.encode(payload, secret, algorithm="HS256")


@router.get("/strava")
async def strava_login():
    """Redirect user to Strava OAuth consent page."""
    client_id = _env("STRAVA_CLIENT_ID")
    redirect_uri = _env("STRAVA_REDIRECT_URI")
    url = (
        "https://www.strava.com/oauth/authorize"
        f"?client_id={client_id}"
        f"&redirect_uri={redirect_uri}"
        "&response_type=code"
        "&scope=activity:read_all"
    )
    return RedirectResponse(url)


@router.get("/strava/callback")
async def strava_callback(code: str = Query(...), error: str | None = Query(None)):
    """Handle OAuth callback: exchange code → upsert user → issue JWT."""
    if error:
        raise HTTPException(status_code=400, detail=f"Strava OAuth error: {error}")

    try:
        tokens = await exchange_code_for_tokens(code)
    except httpx.HTTPStatusError as e:
        # Strava returns useful text, e.g. bad client_secret or redirect_uri mismatch.
        msg = (e.response.text or "")[:300]
        raise HTTPException(
            status_code=502,
            detail=f"Strava token exchange failed: {msg or e.response.status_code}",
        )
    except Exception:
        raise HTTPException(status_code=502, detail="Failed to exchange Strava code")

    athlete = tokens.get("athlete", {})
    strava_id = athlete.get("id")
    if not strava_id:
        raise HTTPException(status_code=502, detail="No athlete data from Strava")

    user_data = {
        "strava_id": strava_id,
        "name": f"{athlete.get('firstname', '')} {athlete.get('lastname', '')}".strip(),
        "avatar_url": athlete.get("profile"),
        "access_token": tokens["access_token"],
        "refresh_token": tokens["refresh_token"],
        "token_expires_at": datetime.fromtimestamp(
            tokens["expires_at"], tz=timezone.utc
        ).isoformat(),
    }

    try:
        supabase = get_supabase()
        result = (
            supabase.table("users")
            .upsert(user_data, on_conflict="strava_id")
            .execute()
        )
    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Failed to save user to Supabase: {str(exc)[:300]}",
        )

    if not result.data:
        raise HTTPException(status_code=500, detail="Failed to save user (empty response)")

    user_id = result.data[0]["id"]
    token = _create_jwt(user_id)

    frontend_callback = f"{frontend_base_url()}/callback"
    return RedirectResponse(f"{frontend_callback}?token={token}")


@router.post("/logout")
async def logout():
    """Stateless logout — client drops the JWT."""
    return {"status": "ok"}
