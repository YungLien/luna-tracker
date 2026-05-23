import os
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import RedirectResponse
from jose import jwt

from app.config import frontend_base_url
from app.db.supabase import get_supabase
from app.services.strava import exchange_code_for_tokens

router = APIRouter(prefix="/auth", tags=["auth"])



def _create_jwt(user_id: str) -> str:
    secret = os.environ["JWT_SECRET"]
    payload = {
        "sub": user_id,
        "exp": datetime.now(timezone.utc) + timedelta(days=30),
    }
    return jwt.encode(payload, secret, algorithm="HS256")


@router.get("/strava")
async def strava_login():
    """Redirect user to Strava OAuth consent page."""
    client_id = os.environ["STRAVA_CLIENT_ID"]
    redirect_uri = os.environ["STRAVA_REDIRECT_URI"]
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
    except Exception as e:
        raise HTTPException(status_code=502, detail="Failed to exchange Strava code")

    athlete = tokens.get("athlete", {})
    strava_id = athlete.get("id")
    if not strava_id:
        raise HTTPException(status_code=502, detail="No athlete data from Strava")

    supabase = get_supabase()

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

    # Upsert by strava_id — creates or updates the user row
    result = (
        supabase.table("users")
        .upsert(user_data, on_conflict="strava_id")
        .execute()
    )

    if not result.data:
        raise HTTPException(status_code=500, detail="Failed to save user")

    user_id = result.data[0]["id"]
    token = _create_jwt(user_id)

    frontend_callback = f"{frontend_base_url()}/callback"
    return RedirectResponse(f"{frontend_callback}?token={token}")


@router.post("/logout")
async def logout():
    """Stateless logout — client drops the JWT."""
    return {"status": "ok"}
