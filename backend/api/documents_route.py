"""Owner-scoped document review, reindexing, and deletion."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from api.auth_middleware import get_current_user
from db.supabase_client import (
    delete_document_db,
    delete_outbound_relationships,
    get_all_documents,
    get_document_by_id,
    store_relationship,
    update_document_metadata,
)
from embeddings.embed_service import embed_chunks
from embeddings.vector_store import add_document_chunks, delete_document
from relationships.relationship_engine import find_relationships
from services.chunking import chunk_extracted_content
from services.review_gate import document_is_graph_eligible

router = APIRouter()


class DocumentUpdate(BaseModel):
    title: str | None = None
    type: str | None = None
    issuer: str | None = None
    date: str | None = None
    skills: list[str] | None = None
    summary: str | None = None
    organization: str | None = None
    location: str | None = None
    technologies: list[str] | None = None
    achievements: list[str] | None = None
    tags: list[str] | None = None


@router.put("/documents/{doc_id}")
async def update_document(doc_id: str, payload: DocumentUpdate, user_id: str = Depends(get_current_user)):
    existing = await get_document_by_id(doc_id, user_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Document not found.")
    updates = {key: value for key, value in payload.model_dump().items() if value is not None}
    updated = await update_document_metadata(doc_id, updates, user_id)
    if not updated:
        raise HTTPException(status_code=500, detail="Document could not be updated.")

    # Rebuild vectors so corrected metadata and content are searchable immediately.
    try:
        await delete_document(doc_id, user_id)
        raw_text = updated.get("raw_text") or updated.get("summary") or ""
        extracted_pages = updated.get("extracted_pages") or [{"page_number": 1, "text": raw_text}]
        chunks = [chunk.to_dict() for chunk in chunk_extracted_content({
            "text": raw_text,
            "pages": extracted_pages,
        })]
        await add_document_chunks(updated, chunks, await embed_chunks(chunks, updated["title"]))
    except Exception as exc:
        print(f"[Documents] Reindex failed: {exc}")

    await delete_outbound_relationships(doc_id, user_id)
    other_docs = [doc for doc in await get_all_documents(user_id=user_id) if str(doc["id"]) != str(doc_id) and document_is_graph_eligible(doc)]
    for relationship in await find_relationships(updated, other_docs):
        await store_relationship(
            relationship["source_id"], relationship["target_id"], relationship["relation_type"],
            relationship["label"], relationship["confidence"], user_id=user_id,
            evidence=relationship.get("evidence"),
        )
    return {"status": "success", "document": updated}


@router.delete("/documents/{doc_id}")
async def remove_document(doc_id: str, user_id: str = Depends(get_current_user)):
    if not await get_document_by_id(doc_id, user_id):
        raise HTTPException(status_code=404, detail="Document not found.")
    await delete_document(doc_id, user_id)
    await delete_outbound_relationships(doc_id, user_id)
    await delete_document_db(doc_id, user_id)
    return {"status": "success", "deleted_id": doc_id}
