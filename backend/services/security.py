"""File validation, filename sanitisation, and trust helpers."""
from __future__ import annotations

import hashlib
import io
import re
import zipfile
from pathlib import Path

from core.config import get_settings

ALLOWED_EXTENSIONS = {".pdf", ".png", ".jpg", ".jpeg", ".webp", ".docx"}


def validate_upload(filename: str, file_bytes: bytes) -> None:
    settings = get_settings()
    extension = Path(filename).suffix.lower()
    if extension not in ALLOWED_EXTENSIONS:
        raise ValueError(f"Unsupported file type: {extension or 'unknown'}")
    if not file_bytes:
        raise ValueError("The uploaded file is empty")
    if len(file_bytes) > settings.max_upload_mb * 1024 * 1024:
        raise ValueError(f"File exceeds the {settings.max_upload_mb} MB limit")
    _validate_signature(extension, file_bytes)


def _validate_signature(extension: str, file_bytes: bytes) -> None:
    if extension == ".pdf" and not file_bytes.startswith(b"%PDF-"):
        raise ValueError("The file extension is PDF, but the content is not a valid PDF.")
    if extension == ".png" and not file_bytes.startswith(b"\x89PNG\r\n\x1a\n"):
        raise ValueError("The file extension is PNG, but the content is not a valid PNG image.")
    if extension in {".jpg", ".jpeg"} and not file_bytes.startswith(b"\xff\xd8\xff"):
        raise ValueError("The file extension is JPEG, but the content is not a valid JPEG image.")
    if extension == ".webp" and not (file_bytes.startswith(b"RIFF") and file_bytes[8:12] == b"WEBP"):
        raise ValueError("The file extension is WEBP, but the content is not a valid WEBP image.")
    if extension == ".docx":
        try:
            with zipfile.ZipFile(io.BytesIO(file_bytes)) as archive:
                names = set(archive.namelist())
                if "[Content_Types].xml" not in names or "word/document.xml" not in names:
                    raise ValueError
        except (zipfile.BadZipFile, ValueError):
            raise ValueError("The file extension is DOCX, but the content is not a valid Word document.")


def sha256_bytes(file_bytes: bytes) -> str:
    return hashlib.sha256(file_bytes).hexdigest()


def safe_filename(filename: str) -> str:
    stem = Path(filename).stem[:80]
    extension = Path(filename).suffix.lower()
    clean = re.sub(r"[^A-Za-z0-9._-]+", "-", stem).strip("-._") or "document"
    return f"{clean}{extension}"
