"""Central configuration for MemoryVerse AI."""
from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache


@dataclass(frozen=True)
class Settings:
    app_name: str = "MemoryVerse AI — Evidence-Backed Career Passport"
    environment: str = os.getenv("APP_ENV", "development")
    allowed_origins: tuple[str, ...] = tuple(
        origin.strip()
        for origin in os.getenv("ALLOWED_ORIGINS", "http://localhost:5173").split(",")
        if origin.strip()
    )
    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")
    generation_model: str = os.getenv("GEMINI_GENERATION_MODEL", "gemini-3.6-flash")
    embedding_model: str = os.getenv("GEMINI_EMBEDDING_MODEL", "gemini-embedding-2")
    supabase_url: str = os.getenv("SUPABASE_URL", "")
    supabase_key: str = os.getenv("SUPABASE_KEY", "")
    storage_bucket: str = os.getenv("SUPABASE_STORAGE_BUCKET", "documents")
    signed_url_ttl_seconds: int = int(os.getenv("SIGNED_URL_TTL_SECONDS", "900"))
    chroma_path: str = os.getenv("CHROMA_PATH", "./chroma_data")
    vector_collection: str = os.getenv("CHROMA_COLLECTION", "memoryverse_evidence_chunks_v4")
    max_upload_mb: int = int(os.getenv("MAX_UPLOAD_MB", "15"))
    chunk_size_chars: int = int(os.getenv("CHUNK_SIZE_CHARS", "2600"))
    chunk_overlap_chars: int = int(os.getenv("CHUNK_OVERLAP_CHARS", "350"))
    rag_top_k: int = int(os.getenv("RAG_TOP_K", "8"))
    rag_candidate_k: int = int(os.getenv("RAG_CANDIDATE_K", "16"))
    rerank_top_k: int = int(os.getenv("RERANK_TOP_K", "8"))
    rerank_enabled: bool = os.getenv("RERANK_ENABLED", "true").strip().lower() in {"1", "true", "yes"}
    graph_expansion_limit: int = int(os.getenv("GRAPH_EXPANSION_LIMIT", "4"))
    review_confidence_threshold: float = float(os.getenv("REVIEW_CONFIDENCE_THRESHOLD", "0.70"))
    github_token: str = os.getenv("GITHUB_TOKEN", "")
    allow_local_fallback: bool = os.getenv("ALLOW_LOCAL_FALLBACK", "false").strip().lower() in {"1", "true", "yes"}

    @property
    def ai_enabled(self) -> bool:
        return bool(self.gemini_api_key)

    @property
    def supabase_enabled(self) -> bool:
        return bool(self.supabase_url and self.supabase_key)


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
