"""Per-user evidence search with semantic and transparent keyword fallback."""
from __future__ import annotations

import re
from fastapi import APIRouter, Depends, Query

from api.auth_middleware import get_current_user
from db.supabase_client import get_all_documents, get_document_by_id
from embeddings.embed_service import embed_query
from embeddings.vector_store import query_similar
from services.review_gate import document_is_graph_eligible

router = APIRouter()


def _keyword_score(query: str, document: dict) -> tuple[int, str]:
    terms = {term for term in re.findall(r"[a-z0-9+#.]{2,}", query.lower())}
    fields = [
        str(document.get("title") or ""),
        str(document.get("summary") or ""),
        str(document.get("issuer") or document.get("organization") or ""),
        " ".join(document.get("skills") or []),
        " ".join(document.get("technologies") or []),
        str(document.get("raw_text") or ""),
    ]
    haystack = " ".join(fields).lower()
    matched = sorted(term for term in terms if term in haystack)
    return len(matched), ", ".join(matched)


async def _keyword_fallback(q: str, user_id: str, doc_type: str | None, limit: int) -> list[dict]:
    documents = [doc for doc in await get_all_documents(user_id=user_id) if document_is_graph_eligible(doc)]
    if doc_type:
        documents = [doc for doc in documents if str(doc.get("type") or "").lower() == doc_type.lower()]
    ranked = []
    for document in documents:
        score, matched = _keyword_score(q, document)
        if score:
            text = document.get("raw_text") or document.get("summary") or ""
            ranked.append({
                "doc_id": str(document["id"]),
                "distance": None,
                "similarity": None,
                "page_number": 1,
                "chunk_index": 0,
                "text": text,
                "document": document,
                "excerpt": " ".join(str(text).split())[:360],
                "retrieval_method": "keyword_fallback",
            "degraded": True,
                "matched_terms": matched,
                "keyword_score": score,
            })
    ranked.sort(key=lambda row: row["keyword_score"], reverse=True)
    return ranked[:limit]


@router.get("/search")
async def search_documents(
    q: str = Query(..., min_length=2, max_length=500),
    type: str | None = Query(default=None),
    limit: int = Query(default=10, ge=1, le=30),
    user_id: str = Depends(get_current_user),
):
    try:
        hits = await query_similar(await embed_query(q), user_id=user_id, n_results=limit, doc_type=type)
        results = []
        for hit in hits:
            document = await get_document_by_id(hit["doc_id"], user_id)
            if document:
                results.append({
                    **hit,
                    "document": document,
                    "excerpt": " ".join((hit.get("text") or "").split())[:360],
                    "retrieval_method": "semantic",
                })
        return {"query": q, "count": len(results), "retrieval_method": "semantic", "degraded": False, "results": results}
    except Exception as exc:
        results = await _keyword_fallback(q, user_id, type, limit)
        return {
            "query": q,
            "count": len(results),
            "retrieval_method": "keyword_fallback",
            "degraded": True,
            "notice": "Semantic embeddings were unavailable; results use transparent keyword matching.",
            "semantic_error": str(exc)[:240],
            "results": results,
        }
