"""Per-user ChromaDB store for page-level evidence chunks."""
from __future__ import annotations

import asyncio
from functools import lru_cache

from core.config import get_settings


@lru_cache(maxsize=1)
def get_collection():
    import chromadb

    settings = get_settings()
    client = chromadb.PersistentClient(path=settings.chroma_path)
    return client.get_or_create_collection(
        name=settings.vector_collection,
        metadata={"hnsw:space": "cosine"},
    )


async def add_document_chunks(document: dict, chunks: list[dict], embeddings: list[list[float]]) -> None:
    if len(chunks) != len(embeddings):
        raise ValueError("Chunk and embedding counts do not match")
    if not chunks:
        return

    ids = [f"{document['id']}:{chunk['chunk_index']}" for chunk in chunks]
    metadatas = []
    for chunk in chunks:
        metadatas.append({
            "user_id": str(document["user_id"]),
            "doc_id": str(document["id"]),
            "title": document.get("title") or "Untitled",
            "type": document.get("type") or "Project",
            "date": str(document.get("date") or ""),
            "page_number": int(chunk.get("page_number") or 0),
            "chunk_index": int(chunk["chunk_index"]),
            "verification_status": document.get("verification_status") or "self_uploaded",
            "review_required": bool(document.get("review_required", False)),
        })

    await asyncio.to_thread(
        get_collection().upsert,
        ids=ids,
        documents=[chunk["text"] for chunk in chunks],
        embeddings=embeddings,
        metadatas=metadatas,
    )


async def query_similar(
    query_embedding: list[float],
    *,
    user_id: str,
    n_results: int = 8,
    doc_type: str | None = None,
) -> list[dict]:
    filters: list[dict] = [{"user_id": str(user_id)}, {"review_required": False}]
    if doc_type:
        filters.append({"type": doc_type})
    where: dict = {"$and": filters}

    results = await asyncio.to_thread(
        get_collection().query,
        query_embeddings=[query_embedding],
        n_results=n_results,
        where=where,
        include=["metadatas", "documents", "distances"],
    )
    return _normalize_query_results(results)


async def get_chunks_for_documents(user_id: str, document_ids: list[str], limit_per_doc: int = 2) -> list[dict]:
    output: list[dict] = []
    collection = get_collection()
    for doc_id in document_ids:
        result = await asyncio.to_thread(
            collection.get,
            where={"$and": [{"user_id": str(user_id)}, {"doc_id": str(doc_id)}]},
            include=["metadatas", "documents"],
        )
        rows = []
        for index, chunk_id in enumerate(result.get("ids") or []):
            metadata = (result.get("metadatas") or [])[index]
            rows.append({
                "chunk_id": chunk_id,
                "doc_id": metadata.get("doc_id"),
                "title": metadata.get("title"),
                "type": metadata.get("type"),
                "date": metadata.get("date"),
                "page_number": metadata.get("page_number") or None,
                "chunk_index": metadata.get("chunk_index"),
                "text": (result.get("documents") or [])[index],
                "similarity": None,
                "retrieval_reason": "graph expansion",
            })
        rows.sort(key=lambda item: item.get("chunk_index") or 0)
        output.extend(rows[:limit_per_doc])
    return output


async def delete_document(doc_id: str, user_id: str | None = None) -> None:
    where = {"doc_id": str(doc_id)}
    if user_id:
        where = {"$and": [{"doc_id": str(doc_id)}, {"user_id": str(user_id)}]}
    await asyncio.to_thread(get_collection().delete, where=where)


async def get_collection_count(user_id: str | None = None) -> int:
    if not user_id:
        return await asyncio.to_thread(get_collection().count)
    result = await asyncio.to_thread(
        get_collection().get,
        where={"user_id": str(user_id)},
        include=["metadatas"],
    )
    return len(result.get("ids") or [])


def _normalize_query_results(results: dict) -> list[dict]:
    ids = (results.get("ids") or [[]])[0]
    metadatas = (results.get("metadatas") or [[]])[0]
    documents = (results.get("documents") or [[]])[0]
    distances = (results.get("distances") or [[]])[0]
    output = []
    for index, chunk_id in enumerate(ids):
        metadata = metadatas[index]
        distance = distances[index]
        output.append({
            "chunk_id": chunk_id,
            "doc_id": metadata.get("doc_id"),
            "title": metadata.get("title"),
            "type": metadata.get("type"),
            "date": metadata.get("date"),
            "page_number": metadata.get("page_number") or None,
            "chunk_index": metadata.get("chunk_index"),
            "verification_status": metadata.get("verification_status"),
            "text": documents[index],
            "similarity": round(max(0.0, 1.0 - float(distance)), 4),
            "retrieval_reason": "semantic search",
        })
    return output
