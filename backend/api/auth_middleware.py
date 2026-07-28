"""Supabase JWT session validation dependency."""
from __future__ import annotations

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
        from db.supabase_client import get_supabase
        supabase = get_supabase()
        response = supabase.auth.get_user(jwt=token)
        user = response.user if hasattr(response, "user") else None
        if not user or not user.id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Your session is invalid or expired. Please sign in again.",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return str(user.id)
    except HTTPException:
        raise
    except Exception as exc:
        error_msg = str(exc).lower()
        if "invalid" in error_msg or "expired" in error_msg or "unauthorized" in error_msg or "jwt" in error_msg:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Your session is invalid or expired. Please sign in again.",
                headers={"WWW-Authenticate": "Bearer"},
            )
        raise HTTPException(status_code=503, detail="Authentication service is temporarily unavailable.")
