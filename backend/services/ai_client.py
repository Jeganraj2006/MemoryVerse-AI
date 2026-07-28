"""Small, testable wrapper around the current Google GenAI SDK."""
from __future__ import annotations

import asyncio
import json
import re
from functools import lru_cache
from typing import Any

from core.config import get_settings


class AIUnavailableError(RuntimeError):
    pass


@lru_cache(maxsize=1)
def _client():
    settings = get_settings()
    if not settings.gemini_api_key:
        raise AIUnavailableError("GEMINI_API_KEY is not configured")
    try:
        from google import genai
    except ImportError as exc:  # pragma: no cover - environment dependent
        raise AIUnavailableError("Install the google-genai package") from exc
    return genai.Client(api_key=settings.gemini_api_key)


def _strip_json_fences(value: str) -> str:
    text = (value or "").strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    return text.strip()


def _generate_text_sync(prompt: str, *, temperature: float, max_output_tokens: int) -> str:
    from google.genai import types

    settings = get_settings()
    response = _client().models.generate_content(
        model=settings.generation_model,
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=temperature,
            max_output_tokens=max_output_tokens,
        ),
    )
    return (response.text or "").strip()


def _generate_json_sync(prompt: str, *, temperature: float, max_output_tokens: int) -> Any:
    from google.genai import types

    settings = get_settings()
    response = _client().models.generate_content(
        model=settings.generation_model,
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=temperature,
            max_output_tokens=max_output_tokens,
            response_mime_type="application/json",
        ),
    )
    return json.loads(_strip_json_fences(response.text or "{}"))


def _embed_sync(text: str) -> list[float]:
    settings = get_settings()
    response = _client().models.embed_content(
        model=settings.embedding_model,
        contents=text,
    )
    embeddings = getattr(response, "embeddings", None) or []
    if not embeddings:
        raise AIUnavailableError("Embedding API returned no vectors")
    values = getattr(embeddings[0], "values", None)
    if values is None and isinstance(embeddings[0], dict):
        values = embeddings[0].get("values")
    if not values:
        raise AIUnavailableError("Embedding API returned an empty vector")
    return [float(value) for value in values]


async def generate_text(prompt: str, *, temperature: float = 0.2, max_output_tokens: int = 1400) -> str:
    return await asyncio.to_thread(
        _generate_text_sync,
        prompt,
        temperature=temperature,
        max_output_tokens=max_output_tokens,
    )


async def generate_json(prompt: str, *, temperature: float = 0.1, max_output_tokens: int = 1800) -> Any:
    return await asyncio.to_thread(
        _generate_json_sync,
        prompt,
        temperature=temperature,
        max_output_tokens=max_output_tokens,
    )


async def embed_text(text: str, *, task: str = "search result", title: str | None = None) -> list[float]:
    clean = " ".join((text or "").split())
    if not clean:
        raise ValueError("Cannot embed empty text")

    if task == "question answering":
        prepared = f"task: question answering | query: {clean}"
    else:
        prepared = f"title: {title or 'none'} | text: {clean}"
    return await asyncio.to_thread(_embed_sync, prepared)
