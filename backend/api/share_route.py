"""Explicit, revocable public portfolio sharing."""
from __future__ import annotations

from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from api.auth_middleware import get_current_user
from db.supabase_client import (
    create_portfolio_share,
    get_all_documents,
    get_all_relationships,
    get_portfolio_share_by_token,
    revoke_portfolio_share,
)
from services.evidence import summarize_evidence
from services.review_gate import document_is_graph_eligible

router = APIRouter()


class CreateShareRequest(BaseModel):
    title: str = Field(default="Evidence-Backed Career Passport", max_length=120)
    document_ids: list[str] = Field(default_factory=list)
    expires_at: str | None = None


@router.post("/shares")
async def create_share(payload: CreateShareRequest, user_id: str = Depends(get_current_user)):
    docs = [doc for doc in await get_all_documents(user_id=user_id) if document_is_graph_eligible(doc)]
    owned = {str(doc["id"]) for doc in docs}
    selected = [doc_id for doc_id in payload.document_ids if doc_id in owned] or list(owned)
    share = await create_portfolio_share(user_id, payload.title, selected, payload.expires_at)
    return {"share": share, "share_path": f"/share/{share['share_token']}"}


@router.delete("/shares/{token}")
async def revoke_share(token: str, user_id: str = Depends(get_current_user)):
    await revoke_portfolio_share(user_id, token)
    return {"status": "revoked"}


@router.get("/public/share/{token}")
async def public_share(token: str):
    share = await get_portfolio_share_by_token(token)
    if not share or share.get("revoked_at"):
        raise HTTPException(status_code=404, detail="This shared career passport is unavailable.")
    if share.get("expires_at") and datetime.fromisoformat(str(share["expires_at"]).replace("Z", "+00:00")) < datetime.now(timezone.utc):
        raise HTTPException(status_code=410, detail="This shared career passport has expired.")

    docs = [doc for doc in await get_all_documents(user_id=str(share["user_id"])) if document_is_graph_eligible(doc)]
    allowed = {str(value) for value in share.get("include_document_ids") or []}
    if allowed:
        docs = [doc for doc in docs if str(doc["id"]) in allowed]
    relationships = await get_all_relationships(str(share["user_id"]))
    document_ids = {str(doc["id"]) for doc in docs}
    relationships = [rel for rel in relationships if str(rel["source_id"]) in document_ids and str(rel["target_id"]) in document_ids]

    # Public payload deliberately excludes raw text, hashes, and storage paths.
    public_docs = [{key: doc.get(key) for key in (
        "id", "title", "type", "issuer", "organization", "date", "skills", "technologies",
        "summary", "source_url", "file_url", "trust_level", "verification_status", "achievements",
    )} for doc in docs]
    return {
        "title": share.get("title"),
        "documents": public_docs,
        "relationships": relationships,
        "evidence": summarize_evidence(public_docs),
    }
