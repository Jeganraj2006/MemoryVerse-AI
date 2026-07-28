"""PDF text extraction with page-level citation support and OCR fallback."""
from __future__ import annotations

import asyncio


async def extract_pdf_text(pdf_path: str, gemini_client=None) -> dict:
    result = await asyncio.to_thread(_extract_pdf_sync, pdf_path)
    if len(result["text"].strip()) >= 80:
        return result

    # Scanned PDF fallback. OCR is optional because Poppler/Tesseract availability varies.
    try:
        from pdf2image import convert_from_path
        from ingestion.ocr_engine import extract_pil_image_text

        images = await asyncio.to_thread(convert_from_path, pdf_path, dpi=220)
        pages = []
        for index, image in enumerate(images, start=1):
            text = await extract_pil_image_text(image, gemini_client=gemini_client)
            pages.append({"page_number": index, "text": text.strip()})
        combined = "\n\n".join(page["text"] for page in pages if page["text"])
        return {
            "text": combined,
            "method": "ocr",
            "page_count": len(pages),
            "pages": pages,
        }
    except Exception as exc:
        result["warning"] = f"OCR fallback unavailable: {exc}"
        return result


def _extract_pdf_sync(pdf_path: str) -> dict:
    import pdfplumber

    pages = []
    with pdfplumber.open(pdf_path) as pdf:
        for index, page in enumerate(pdf.pages, start=1):
            pages.append({
                "page_number": index,
                "text": (page.extract_text() or "").strip(),
            })
    combined = "\n\n".join(page["text"] for page in pages if page["text"])
    return {
        "text": combined,
        "method": "pdfplumber",
        "page_count": len(pages),
        "pages": pages,
    }
