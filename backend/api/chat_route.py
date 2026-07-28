"""Grounded Graph-RAG chat endpoint."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from api.auth_middleware import get_current_user
from retrieval.rag_query import answer_query

router = APIRouter()


class ChatRequest(BaseModel):
    question: str = Field(min_length=2, max_length=1500)
    conversation_history: list[dict] = Field(default_factory=list)


@router.post("/chat")
async def chat(request: ChatRequest, user_id: str = Depends(get_current_user)):
    try:
        return await answer_query(
            request.question,
            user_id=user_id,
            conversation_history=request.conversation_history,
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Evidence retrieval failed: {exc}")
