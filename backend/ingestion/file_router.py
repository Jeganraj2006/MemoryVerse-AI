"""Validate and route supported files to page-aware text extractors."""
from __future__ import annotations

import os
import tempfile
from pathlib import Path

SUPPORTED_EXTENSIONS = {".pdf", ".png", ".jpg", ".jpeg", ".webp", ".docx"}


def get_file_type(filename: str) -> str:
    extension = Path(filename).suffix.lower()
    if extension == ".pdf":
        return "pdf"
    if extension in {".png", ".jpg", ".jpeg", ".webp"}:
        return "image"
    if extension == ".docx":
        return "docx"
    raise ValueError(f"Unsupported file type: {extension}. Supported: {', '.join(sorted(SUPPORTED_EXTENSIONS))}")


async def extract_text(file_bytes: bytes, filename: str, gemini_client=None) -> dict:
    file_type = get_file_type(filename)
    suffix = Path(filename).suffix.lower()
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as temporary:
        temporary.write(file_bytes)
        temporary_path = temporary.name

    try:
        if file_type == "pdf":
            from ingestion.pdf_parser import extract_pdf_text
            return await extract_pdf_text(temporary_path, gemini_client=gemini_client)
        if file_type == "image":
            from ingestion.ocr_engine import extract_image_text
            return await extract_image_text(temporary_path, gemini_client=gemini_client)
        from ingestion.docx_parser import extract_docx_text
        return await extract_docx_text(temporary_path)
    finally:
        try:
            os.unlink(temporary_path)
        except OSError:
            pass
