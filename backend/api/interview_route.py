"""Portfolio-grounded interview practice with conservative, transparent feedback."""
from __future__ import annotations

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from api.auth_middleware import get_current_user
from db.supabase_client import get_all_documents, store_interview_history
from services.ai_client import generate_json

router = APIRouter()


class Submit(BaseModel):
    submissions: list[dict] = Field(default_factory=list, max_length=10)


@router.get("/interview/generate-questions")
async def questions(user_id: str = Depends(get_current_user)):
    documents = await get_all_documents(user_id=user_id)
    evidence = [
        {
            "id": document.get("id"),
            "title": document.get("title"),
            "type": document.get("type"),
            "skills": document.get("skills") or [],
            "summary": document.get("summary"),
        }
        for document in documents[:12]
    ]
    try:
        result = await generate_json(
            "Generate exactly five interview questions grounded in this portfolio. "
            "Include project depth, evidence verification, and one behavioral question. "
            "Return JSON with a questions array. Each item must have id, question, category, and evidence_document_id. "
            f"Portfolio: {evidence}",
            temperature=0.15,
        )
        rows = result if isinstance(result, list) else result.get("questions", [])
    except Exception:
        rows = []

    normalized = _normalize_questions(rows, documents)
    if len(normalized) < 5:
        normalized.extend(_fallback_questions(documents, start=len(normalized) + 1))
    return {"questions": normalized[:5], "methodology": "Questions are grounded in owned portfolio evidence."}


@router.post("/interview/submit-answers")
async def grade(payload: Submit, user_id: str = Depends(get_current_user)):
    submissions = payload.submissions[:10]
    try:
        result = await generate_json(
            "Grade these interview answers conservatively. Do not reward unsupported claims. "
            "Return JSON with overall_score from 0 to 100, feedback, and detailed_grades. "
            "Each detailed grade must contain question_text, score from 0 to 100, feedback, and ideal_response. "
            "Treat the score as coaching feedback, not a hiring prediction. "
            f"Answers: {submissions}",
            temperature=0.1,
        )
    except Exception:
        result = {
            "overall_score": 0,
            "feedback": "AI grading is unavailable. Review each answer for STAR structure, technical depth, measurable outcomes, and direct evidence.",
            "detailed_grades": [
                {
                    "question_text": str(item.get("question_text") or "Interview question"),
                    "score": 0,
                    "feedback": "Automated feedback unavailable.",
                    "ideal_response": "State the context, your exact action, the result, and the portfolio evidence supporting the claim.",
                }
                for item in submissions
            ],
        }
    normalized = _normalize_grades(result, submissions)
    await store_interview_history({key: normalized[key] for key in ("overall_score", "feedback", "detailed_grades")}, user_id)
    return normalized


def _normalize_questions(rows: list, documents: list[dict]) -> list[dict]:
    owned_ids = {str(document.get("id")) for document in documents}
    output = []
    for index, row in enumerate(rows or [], start=1):
        if not isinstance(row, dict):
            continue
        text = str(row.get("question") or row.get("text") or "").strip()
        if not text:
            continue
        evidence_id = str(row.get("evidence_document_id") or "")
        output.append({
            "id": row.get("id") or index,
            "question": text,
            "category": str(row.get("category") or row.get("type") or "Evidence"),
            "evidence_document_id": evidence_id if evidence_id in owned_ids else None,
        })
    return output


def _fallback_questions(documents: list[dict], start: int = 1) -> list[dict]:
    rows = []
    for document in documents[:3]:
        rows.append({
            "id": start + len(rows),
            "question": f"Explain your work in {document['title']} and identify the strongest evidence of your contribution.",
            "category": document.get("type") or "Project",
            "evidence_document_id": document.get("id"),
        })
    generic = [
        ("Describe a challenge using the STAR method and connect it to a portfolio item.", "Behavioral"),
        ("Which skill in your portfolio has the strongest evidence, and what still needs stronger proof?", "Evidence"),
        ("Describe one technical decision you would change if you rebuilt your strongest project.", "Technical"),
        ("How do you distinguish a claimed skill from a demonstrated or applied skill?", "Evidence"),
        ("Walk through one project from problem definition to measurable result.", "Project"),
    ]
    for text, category in generic:
        rows.append({"id": start + len(rows), "question": text, "category": category, "evidence_document_id": None})
    return rows


def _normalize_grades(result: dict, submissions: list[dict]) -> dict:
    try:
        overall = int(float(result.get("overall_score", 0)))
    except (TypeError, ValueError):
        overall = 0
    detailed = []
    raw_grades = result.get("detailed_grades") or []
    for index, submission in enumerate(submissions):
        row = raw_grades[index] if index < len(raw_grades) and isinstance(raw_grades[index], dict) else {}
        try:
            score = int(float(row.get("score", 0)))
        except (TypeError, ValueError):
            score = 0
        detailed.append({
            "question_text": str(row.get("question_text") or submission.get("question_text") or "Interview question"),
            "score": max(0, min(100, score)),
            "feedback": str(row.get("feedback") or "Explain your exact contribution and connect it to verifiable evidence."),
            "ideal_response": str(row.get("ideal_response") or "Use context, action, measurable result, and supporting portfolio evidence."),
        })
    return {
        "overall_score": max(0, min(100, overall)),
        "feedback": str(result.get("feedback") or "This score is coaching feedback, not a hiring prediction."),
        "detailed_grades": detailed,
        "methodology": "Conservative AI coaching score; not a validated hiring assessment.",
    }
