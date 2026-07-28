"""Supabase JWT session validation dependency."""
from __future__ import annotations

import httpx
from fastapi import HTTPException, Request, status

from core.config import get_settings


async def get_current_user(request: Request) -> str:
    authorization = request.headers.get("Authorization", "")
    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Please sign in to access your private career passport.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    settings = get_settings()
    if not settings.supabase_enabled:
        raise HTTPException(status_code=503, detail="Authentication service is not configured.")

    token = authorization.removeprefix("Bearer ").strip()
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(
                f"{settings.supabase_url}/auth/v1/user",
                headers={"Authorization": f"Bearer {token}", "apikey": settings.supabase_key},
            )
        if response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Your session is invalid or expired. Please sign in again.",
                headers={"WWW-Authenticate": "Bearer"},
            )
        user_id = response.json().get("id")
        if not user_id:
            raise HTTPException(status_code=401, detail="The authenticated user could not be identified.")
        return str(user_id)
    except HTTPException:
        raise
    except httpx.HTTPError:
        raise HTTPException(status_code=503, detail="Authentication service is temporarily unavailable.")
