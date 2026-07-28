"""Page-aware text chunking with stable citation metadata."""
from __future__ import annotations

import re
from dataclasses import dataclass, asdict

from core.config import get_settings


@dataclass
class TextChunk:
    chunk_index: int
    page_number: int | None
    text: str
    char_start: int
    char_end: int

    def to_dict(self) -> dict:
        return asdict(self)


def _split_long_text(text: str, size: int, overlap: int) -> list[tuple[str, int, int]]:
    normalized = re.sub(r"[ \t]+", " ", (text or "")).strip()
    if not normalized:
        return []

    pieces: list[tuple[str, int, int]] = []
    start = 0
    while start < len(normalized):
        proposed_end = min(len(normalized), start + size)
        end = proposed_end
        if proposed_end < len(normalized):
            boundary = max(
                normalized.rfind("\n", start, proposed_end),
                normalized.rfind(". ", start, proposed_end),
                normalized.rfind("; ", start, proposed_end),
            )
            if boundary > start + size // 2:
                end = boundary + 1
        text_piece = normalized[start:end].strip()
        if text_piece:
            pieces.append((text_piece, start, end))
        if end >= len(normalized):
            break
        start = max(end - overlap, start + 1)
    return pieces


def chunk_extracted_content(extracted: dict) -> list[TextChunk]:
    settings = get_settings()
    pages = extracted.get("pages") or []
    if not pages:
        pages = [{"page_number": 1, "text": extracted.get("text", "")}]

    chunks: list[TextChunk] = []
    index = 0
    for page in pages:
        page_number = page.get("page_number")
        for text, start, end in _split_long_text(
            page.get("text", ""),
            settings.chunk_size_chars,
            settings.chunk_overlap_chars,
        ):
            chunks.append(TextChunk(index, page_number, text, start, end))
            index += 1
    return chunks
