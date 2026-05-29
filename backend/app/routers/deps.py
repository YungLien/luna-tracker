import asyncio
import os
from typing import Any

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt

from app.db.supabase import get_supabase

bearer = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer),
) -> dict[str, Any]:
    """Verify JWT and return the user row from Supabase."""
    token = credentials.credentials
    secret = os.environ["JWT_SECRET"]

    try:
        payload = jwt.decode(token, secret, algorithms=["HS256"])
        user_id: str = payload.get("sub")
        if not user_id:
            raise ValueError("No sub in token")
    except (JWTError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )

    supabase = get_supabase()
    result = await asyncio.to_thread(
        lambda: supabase.table("users").select("*").eq("id", user_id).execute()
    )

    if not result.data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    return result.data[0]
