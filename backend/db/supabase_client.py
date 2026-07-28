"""Secure persistence helpers for MemoryVerse AI.

All portfolio records are scoped by ``user_id``. Supabase is preferred; a small
local JSON fallback is retained only for offline demos and applies the same
ownership filters.
"""
from __future__ import annotations

import json
import mimetypes
import os
import uuid
from datetime import datetime, timezone
from functools import lru_cache
from pathlib import Path
from typing import Optional

from core.config import get_settings
from services.security import safe_filename

LOCAL_DB_FILE = Path(__file__).with_name("local_db.json")
CORE_TYPES = {"Certification", "Project", "Internship", "Achievement", "Academic", "Skill"}


def _require_explicit_local_fallback(exc: Exception, context: str) -> None:
    """Prevent silent data downgrades unless the owner explicitly enabled demo fallback."""
    if not get_settings().allow_local_fallback:
        raise RuntimeError(f"{context} failed and local fallback is disabled") from exc
    print(f"[Persistence] {context} failed; using explicit local fallback: {exc}")


@lru_cache(maxsize=1)
def get_supabase():
    settings = get_settings()
    if not settings.supabase_enabled:
        raise RuntimeError("Supabase is not configured")
    from supabase import create_client

    return create_client(settings.supabase_url, settings.supabase_key)


def map_to_core_type(value: str | None) -> str:
    aliases = {
        "Certificate": "Certification",
        "Certification": "Certification",
        "Resume": "Skill",
        "Marksheet": "Academic",
        "Academic": "Academic",
        "Passport": "Academic",
        "Internship": "Internship",
        "Research Paper": "Project",
        "Project": "Project",
        "Invoice": "Achievement",
        "Identity Card": "Academic",
        "Email": "Achievement",
        "Letter": "Achievement",
        "Receipt": "Achievement",
        "Achievement": "Achievement",
        "Skill": "Skill",
        "GitHub Repository": "Project",
    }
    mapped = aliases.get(value or "", "Project")
    return mapped if mapped in CORE_TYPES else "Project"


def _load_local_db() -> dict:
    if not LOCAL_DB_FILE.exists():
        return {}
    try:
        return json.loads(LOCAL_DB_FILE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _save_local_db(database: dict) -> None:
    LOCAL_DB_FILE.write_text(json.dumps(database, indent=2, default=str), encoding="utf-8")


def _local_rows(table: str) -> list[dict]:
    return list(_load_local_db().get(table, []))


def _local_insert(table: str, row: dict) -> dict:
    database = _load_local_db()
    record = dict(row)
    record.setdefault("id", str(uuid.uuid4()))
    record.setdefault("created_at", datetime.now(timezone.utc).isoformat())
    database.setdefault(table, []).append(record)
    _save_local_db(database)
    return record


def _local_update(table: str, record_id: str, user_id: str, updates: dict) -> dict:
    database = _load_local_db()
    for record in database.get(table, []):
        if str(record.get("id")) == str(record_id) and str(record.get("user_id")) == str(user_id):
            record.update(updates)
            record["updated_at"] = datetime.now(timezone.utc).isoformat()
            _save_local_db(database)
            return record
    return {}


def _local_delete(table: str, predicate) -> None:
    database = _load_local_db()
    database[table] = [row for row in database.get(table, []) if not predicate(row)]
    _save_local_db(database)


async def store_document(metadata: dict, file_bytes: bytes, filename: str) -> dict:
    user_id = str(metadata.get("user_id") or "")
    if not user_id:
        raise ValueError("user_id is required when storing a document")

    settings = get_settings()
    document_id = str(uuid.uuid4())
    clean_name = safe_filename(filename)
    storage_path = f"{user_id}/{document_id}/{clean_name}" if file_bytes else None

    row = {
        "id": document_id,
        "user_id": user_id,
        "title": metadata.get("title") or Path(filename).stem,
        "type": map_to_core_type(metadata.get("type")),
        "issuer": metadata.get("issuer"),
        "date": metadata.get("date"),
        "skills": metadata.get("skills") or [],
        "summary": metadata.get("summary") or "",
        "raw_text": metadata.get("raw_text") or "",
        "extracted_pages": metadata.get("extracted_pages") or [],
        "confidence": float(metadata.get("confidence", 0.5)),
        "organization": metadata.get("organization"),
        "location": metadata.get("location"),
        "technologies": metadata.get("technologies") or [],
        "experience": metadata.get("experience"),
        "achievements": metadata.get("achievements") or [],
        "tags": metadata.get("tags") or [],
        "source_kind": metadata.get("source_kind", "file"),
        "source_url": metadata.get("source_url"),
        "storage_path": storage_path,
        "file_hash": metadata.get("file_hash"),
        "original_filename": filename,
        "mime_type": metadata.get("mime_type") or mimetypes.guess_type(filename)[0],
        "page_count": int(metadata.get("page_count") or 1),
        "trust_level": metadata.get("trust_level", "self_uploaded"),
        "verification_status": metadata.get("verification_status", "self_uploaded"),
        "verification_details": metadata.get("verification_details") or {},
        "review_required": bool(metadata.get("review_required", False)),
        "fields_needing_review": metadata.get("fields_needing_review") or [],
    }

    try:
        supabase = get_supabase()
        if file_bytes and storage_path:
            supabase.storage.from_(settings.storage_bucket).upload(
                path=storage_path,
                file=file_bytes,
                file_options={
                    "content-type": row["mime_type"] or "application/octet-stream",
                    "upsert": "false",
                },
            )
        result = supabase.table("documents").insert(row).execute()
        stored = result.data[0]
        return await _hydrate_signed_url(stored)
    except Exception as exc:
        _require_explicit_local_fallback(exc, "Supabase document/storage write")
        return _local_insert("documents", row)


async def find_document_by_hash(user_id: str, file_hash: str) -> Optional[dict]:
    if not file_hash:
        return None
    try:
        result = (
            get_supabase().table("documents").select("*")
            .eq("user_id", user_id).eq("file_hash", file_hash).limit(1).execute()
        )
        return await _hydrate_signed_url(result.data[0]) if result.data else None
    except Exception as exc:
        _require_explicit_local_fallback(exc, "Supabase duplicate lookup")
        return next((row for row in _local_rows("documents") if row.get("user_id") == user_id and row.get("file_hash") == file_hash), None)


async def get_all_documents(limit: int = 200, user_id: str | None = None) -> list[dict]:
    if not user_id:
        return []
    try:
        result = (
            get_supabase().table("documents").select("*")
            .eq("user_id", user_id)
            .order("date", desc=True, nullsfirst=False)
            .limit(limit).execute()
        )
        return [await _hydrate_signed_url(row) for row in result.data]
    except Exception as exc:
        _require_explicit_local_fallback(exc, "Supabase document listing")
        rows = [row for row in _local_rows("documents") if str(row.get("user_id")) == str(user_id)]
        rows.sort(key=lambda row: row.get("date") or row.get("created_at") or "", reverse=True)
        return rows[:limit]


async def get_document_by_id(doc_id: str, user_id: str | None = None) -> Optional[dict]:
    if not user_id:
        return None
    try:
        result = (
            get_supabase().table("documents").select("*")
            .eq("id", doc_id).eq("user_id", user_id).limit(1).execute()
        )
        return await _hydrate_signed_url(result.data[0]) if result.data else None
    except Exception as exc:
        _require_explicit_local_fallback(exc, "Supabase document read")
        return next((row for row in _local_rows("documents") if str(row.get("id")) == str(doc_id) and str(row.get("user_id")) == str(user_id)), None)


async def update_document_metadata(doc_id: str, updates: dict, user_id: str | None = None) -> dict:
    if not user_id:
        return {}
    allowed = {
        "title", "type", "issuer", "date", "skills", "summary", "organization",
        "location", "technologies", "experience", "achievements", "tags",
        "verification_status", "verification_details", "trust_level", "review_required",
        "fields_needing_review",
    }
    sanitized = {key: value for key, value in updates.items() if key in allowed}
    if "type" in sanitized:
        sanitized["type"] = map_to_core_type(sanitized["type"])
    sanitized["confidence"] = 1.0
    sanitized["review_required"] = False
    sanitized["fields_needing_review"] = []
    sanitized["updated_at"] = datetime.now(timezone.utc).isoformat()

    try:
        result = (
            get_supabase().table("documents").update(sanitized)
            .eq("id", doc_id).eq("user_id", user_id).execute()
        )
        return await _hydrate_signed_url(result.data[0]) if result.data else {}
    except Exception as exc:
        _require_explicit_local_fallback(exc, "Supabase document update")
        return _local_update("documents", doc_id, user_id, sanitized)


async def delete_document_db(doc_id: str, user_id: str | None = None) -> None:
    if not user_id:
        return
    document = await get_document_by_id(doc_id, user_id)
    try:
        supabase = get_supabase()
        if document and document.get("storage_path"):
            supabase.storage.from_(get_settings().storage_bucket).remove([document["storage_path"]])
        supabase.table("documents").delete().eq("id", doc_id).eq("user_id", user_id).execute()
    except Exception as exc:
        _require_explicit_local_fallback(exc, "Supabase document delete")
        _local_delete("documents", lambda row: str(row.get("id")) == str(doc_id) and str(row.get("user_id")) == str(user_id))


async def store_relationship(
    source_id: str,
    target_id: str,
    relation_type: str,
    label: str,
    confidence: float = 0.8,
    *,
    user_id: str | None = None,
    evidence: dict | None = None,
) -> dict:
    if not user_id:
        raise ValueError("user_id is required for relationships")
    row = {
        "user_id": user_id,
        "source_id": source_id,
        "target_id": target_id,
        "relation_type": relation_type,
        "label": label,
        "confidence": confidence,
        "evidence": evidence or {},
    }
    try:
        result = get_supabase().table("relationships").upsert(
            row,
            on_conflict="user_id,source_id,target_id,relation_type",
        ).execute()
        return result.data[0]
    except Exception as exc:
        _require_explicit_local_fallback(exc, "Supabase relationship write")
        existing = next((item for item in _local_rows("relationships") if all(str(item.get(key)) == str(row.get(key)) for key in ("user_id", "source_id", "target_id", "relation_type"))), None)
        return existing or _local_insert("relationships", row)


async def get_all_relationships(user_id: str | None = None) -> list[dict]:
    if not user_id:
        return []
    try:
        return get_supabase().table("relationships").select("*").eq("user_id", user_id).execute().data
    except Exception as exc:
        _require_explicit_local_fallback(exc, "Supabase relationship listing")
        return [row for row in _local_rows("relationships") if str(row.get("user_id")) == str(user_id)]


async def get_relationships_for_documents(user_id: str, document_ids: list[str]) -> list[dict]:
    relationships = await get_all_relationships(user_id)
    ids = {str(value) for value in document_ids}
    return [row for row in relationships if str(row.get("source_id")) in ids or str(row.get("target_id")) in ids]


async def delete_outbound_relationships(doc_id: str, user_id: str | None = None) -> None:
    if not user_id:
        return
    try:
        get_supabase().table("relationships").delete().eq("user_id", user_id).or_(f"source_id.eq.{doc_id},target_id.eq.{doc_id}").execute()
    except Exception as exc:
        _require_explicit_local_fallback(exc, "Supabase relationship delete")
        _local_delete("relationships", lambda row: str(row.get("user_id")) == str(user_id) and (str(row.get("source_id")) == str(doc_id) or str(row.get("target_id")) == str(doc_id)))


async def _hydrate_signed_url(document: dict) -> dict:
    row = dict(document)
    row["file_url"] = row.get("source_url")
    storage_path = row.get("storage_path")
    if not storage_path:
        return row
    try:
        signed = get_supabase().storage.from_(get_settings().storage_bucket).create_signed_url(
            storage_path,
            get_settings().signed_url_ttl_seconds,
        )
        row["file_url"] = signed.get("signedURL") or signed.get("signed_url")
    except Exception as exc:
        print(f"[Storage] Could not create signed URL: {exc}")
    return row


async def _store_user_record(table: str, payload: dict, user_id: str | None) -> dict:
    if not user_id:
        raise ValueError("user_id is required")
    row = {**payload, "user_id": user_id}
    try:
        result = get_supabase().table(table).insert(row).execute()
        return result.data[0]
    except Exception as exc:
        _require_explicit_local_fallback(exc, f"Supabase {table} write")
        return _local_insert(table, row)


async def _list_user_records(table: str, user_id: str | None) -> list[dict]:
    if not user_id:
        return []
    try:
        return get_supabase().table(table).select("*").eq("user_id", user_id).order("created_at", desc=True).execute().data
    except Exception as exc:
        _require_explicit_local_fallback(exc, f"Supabase {table} listing")
        return [row for row in _local_rows(table) if str(row.get("user_id")) == str(user_id)]


async def store_career_analysis(analysis: dict, user_id: str | None = None) -> dict:
    return await _store_user_record("career_analyses", analysis, user_id)


async def get_latest_career_analysis(user_id: str | None = None) -> Optional[dict]:
    rows = await _list_user_records("career_analyses", user_id)
    return rows[0] if rows else None


async def store_resume_version(resume: dict, user_id: str | None = None) -> dict:
    return await _store_user_record("resume_versions", resume, user_id)


async def get_resume_versions(user_id: str | None = None) -> list[dict]:
    return await _list_user_records("resume_versions", user_id)


async def store_portfolio_version(portfolio: dict, user_id: str | None = None) -> dict:
    return await _store_user_record("portfolio_versions", portfolio, user_id)


async def get_portfolio_versions(user_id: str | None = None) -> list[dict]:
    return await _list_user_records("portfolio_versions", user_id)


async def store_interview_history(interview: dict, user_id: str | None = None) -> dict:
    return await _store_user_record("mock_interviews", interview, user_id)


async def get_interview_histories(user_id: str | None = None) -> list[dict]:
    return await _list_user_records("mock_interviews", user_id)

async def create_portfolio_share(user_id: str, title: str, include_document_ids: list[str], expires_at: str | None = None) -> dict:
    row = {
        "user_id": user_id,
        "title": title,
        "include_document_ids": include_document_ids,
        "expires_at": expires_at,
    }
    try:
        result = get_supabase().table("portfolio_shares").insert(row).execute()
        return result.data[0]
    except Exception as exc:
        _require_explicit_local_fallback(exc, "Supabase portfolio share creation")
        row["share_token"] = uuid.uuid4().hex + uuid.uuid4().hex[:16]
        return _local_insert("portfolio_shares", row)


async def get_portfolio_share_by_token(token: str) -> Optional[dict]:
    try:
        result = get_supabase().table("portfolio_shares").select("*").eq("share_token", token).limit(1).execute()
        return result.data[0] if result.data else None
    except Exception as exc:
        _require_explicit_local_fallback(exc, "Supabase public share lookup")
        return next((row for row in _local_rows("portfolio_shares") if row.get("share_token") == token), None)


async def revoke_portfolio_share(user_id: str, token: str) -> None:
    revoked_at = datetime.now(timezone.utc).isoformat()
    try:
        get_supabase().table("portfolio_shares").update({"revoked_at": revoked_at}).eq("user_id", user_id).eq("share_token", token).execute()
    except Exception as exc:
        _require_explicit_local_fallback(exc, "Supabase portfolio share revocation")
        database = _load_local_db()
        for row in database.get("portfolio_shares", []):
            if row.get("user_id") == user_id and row.get("share_token") == token:
                row["revoked_at"] = revoked_at
        _save_local_db(database)
