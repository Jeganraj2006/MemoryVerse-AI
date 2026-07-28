"""Chunk-level embeddings for evidence retrieval."""
from __future__ import annotations

from services.ai_client import AIUnavailableError, embed_text


async def embed_chunks(chunks: list[dict], title: str) -> list[list[float]]:
    vectors: list[list[float]] = []
    for chunk in chunks:
        vectors.append(await embed_text(chunk["text"], task="search result", title=title))
    return vectors


async def embed_query(query: str) -> list[float]:
    return await embed_text(query, task="question answering")


async def embed_document(document: dict) -> list[float]:
    """Compatibility helper for modules that need one document-level vector."""
    text = "\n".join(filter(None, [
        document.get("title"),
        document.get("summary"),
        ", ".join(document.get("skills") or []),
        ", ".join(document.get("technologies") or []),
    ]))
    return await embed_text(text, task="search result", title=document.get("title"))


__all__ = ["AIUnavailableError", "embed_chunks", "embed_query", "embed_document"]
