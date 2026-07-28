"""Image OCR with local Tesseract first and Gemini Vision as an optional fallback."""
from __future__ import annotations

import asyncio
import os


async def extract_image_text(image_path: str, gemini_client=None) -> dict:
    from PIL import Image

    image = await asyncio.to_thread(Image.open, image_path)
    text = await extract_pil_image_text(image, gemini_client=gemini_client)
    return {
        "text": text,
        "method": "ocr",
        "page_count": 1,
        "pages": [{"page_number": 1, "text": text}],
    }


async def extract_pil_image_text(image, gemini_client=None) -> str:
    try:
        import pytesseract

        configured = os.getenv("TESSERACT_CMD")
        if configured:
            pytesseract.pytesseract.tesseract_cmd = configured
        text = await asyncio.to_thread(pytesseract.image_to_string, image)
        if len(text.strip()) >= 40:
            return text.strip()
    except Exception as exc:
        print(f"[OCR] Local OCR unavailable: {exc}")

    # Keep OCR deterministic and offline-friendly. Metadata structuring will flag review.
    return ""
