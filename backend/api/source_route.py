"""Trusted source ingestion, starting with public GitHub repositories."""
from __future__ import annotations

import base64
import re
from urllib.parse import urlparse

import httpx
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, HttpUrl

from api.auth_middleware import get_current_user
from core.config import get_settings
from db.supabase_client import find_document_by_hash, get_all_documents, store_document, store_relationship
from embeddings.embed_service import embed_chunks
from embeddings.vector_store import add_document_chunks
from relationships.relationship_engine import find_relationships
from services.chunking import chunk_extracted_content
from services.security import sha256_bytes

router = APIRouter()


class GitHubImportRequest(BaseModel):
    url: HttpUrl


@router.post("/sources/github")
async def import_github_repository(payload: GitHubImportRequest, user_id: str = Depends(get_current_user)):
    owner, repository = _parse_repository_url(str(payload.url))
    settings = get_settings()
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2026-03-10",
        "User-Agent": "MemoryVerse-AI",
    }
    if settings.github_token:
        headers["Authorization"] = f"Bearer {settings.github_token}"

    async with httpx.AsyncClient(timeout=20, headers=headers, follow_redirects=True) as client:
        repo_response = await client.get(f"https://api.github.com/repos/{owner}/{repository}")
        if repo_response.status_code == 404:
            raise HTTPException(status_code=404, detail="Public GitHub repository not found.")
        if repo_response.status_code != 200:
            raise HTTPException(status_code=502, detail=f"GitHub returned {repo_response.status_code}.")
        repo = repo_response.json()
        language_response = await client.get(repo["languages_url"])
        languages = list(language_response.json().keys()) if language_response.status_code == 200 else []
        readme_response = await client.get(f"https://api.github.com/repos/{owner}/{repository}/readme")

    readme = ""
    if readme_response.status_code == 200:
        encoded = readme_response.json().get("content") or ""
        readme = base64.b64decode(encoded).decode("utf-8", errors="replace")

    canonical_url = repo.get("html_url") or str(payload.url)
    fingerprint = sha256_bytes(f"github:{repo.get('id')}".encode())
    duplicate = await find_document_by_hash(user_id, fingerprint)
    if duplicate:
        raise HTTPException(status_code=409, detail=f"This repository is already imported as '{duplicate['title']}'.")

    text = "\n".join(filter(None, [
        f"Repository: {repo.get('full_name')}",
        f"Description: {repo.get('description') or ''}",
        f"Languages: {', '.join(languages)}",
        f"Topics: {', '.join(repo.get('topics') or [])}",
        f"Homepage: {repo.get('homepage') or ''}",
        "README:",
        readme[:30000],
    ]))
    extracted = {"text": text, "pages": [{"page_number": 1, "text": text}], "page_count": 1, "method": "github_api"}
    chunks = [chunk.to_dict() for chunk in chunk_extracted_content(extracted)]
    metadata = {
        "user_id": user_id,
        "title": repo.get("name") or repository,
        "type": "Project",
        "issuer": "GitHub",
        "organization": repo.get("owner", {}).get("login"),
        "date": (repo.get("pushed_at") or repo.get("updated_at") or "")[:10] or None,
        "skills": languages,
        "technologies": list(repo.get("topics") or []),
        "summary": repo.get("description") or f"Source-linked GitHub project {repo.get('full_name')}.",
        "raw_text": text,
        "extracted_pages": extracted["pages"],
        "confidence": 0.95,
        "tags": ["github", "source-linked", *(repo.get("topics") or [])][:12],
        "source_kind": "github",
        "source_url": canonical_url,
        "file_hash": fingerprint,
        "page_count": 1,
        "mime_type": "text/markdown",
        "trust_level": "source_linked",
        "verification_status": "source_linked",
        "verification_details": {
            "github_repository_id": repo.get("id"),
            "owner": owner,
            "repository": repository,
            "default_branch": repo.get("default_branch"),
            "pushed_at": repo.get("pushed_at"),
            "fork": repo.get("fork", False),
        },
        "review_required": False,
    }
    stored = await store_document(metadata, readme.encode("utf-8"), f"{repository}-README.md")
    try:
        await add_document_chunks(stored, chunks, await embed_chunks(chunks, stored["title"]))
    except Exception as exc:
        print(f"[GitHub] Indexing failed: {exc}")

    existing = [doc for doc in await get_all_documents(user_id=user_id) if str(doc["id"]) != str(stored["id"])]
    for relationship in await find_relationships(stored, existing):
        await store_relationship(
            relationship["source_id"], relationship["target_id"], relationship["relation_type"],
            relationship["label"], relationship["confidence"], user_id=user_id,
            evidence=relationship.get("evidence"),
        )
    return {"status": "success", "document": stored, "processing": {"chunk_count": len(chunks), "source": "GitHub REST API"}}


def _parse_repository_url(url: str) -> tuple[str, str]:
    parsed = urlparse(url)
    if parsed.netloc.casefold() not in {"github.com", "www.github.com"}:
        raise HTTPException(status_code=400, detail="Enter a github.com repository URL.")
    parts = [part for part in parsed.path.split("/") if part]
    if len(parts) < 2:
        raise HTTPException(status_code=400, detail="The URL must include an owner and repository.")
    owner, repository = parts[0], re.sub(r"\.git$", "", parts[1])
    if not re.fullmatch(r"[A-Za-z0-9_.-]+", owner) or not re.fullmatch(r"[A-Za-z0-9_.-]+", repository):
        raise HTTPException(status_code=400, detail="Invalid GitHub repository URL.")
    return owner, repository
