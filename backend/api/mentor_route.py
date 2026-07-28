"""Evidence-grounded career coaching without hiring or salary predictions."""
from __future__ import annotations

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from api.auth_middleware import get_current_user
from db.supabase_client import get_all_documents
from services.ai_client import generate_json
from services.evidence import summarize_evidence
from services.review_gate import document_is_graph_eligible

router = APIRouter()


class MentorRequest(BaseModel):
    goal: str = Field(min_length=3, max_length=2000)
    conversation_history: list[dict] = Field(default_factory=list)


@router.post("/career-mentor/chat")
async def mentor(payload: MentorRequest, user_id: str = Depends(get_current_user)):
    documents = [doc for doc in await get_all_documents(user_id=user_id) if document_is_graph_eligible(doc)]
    evidence = summarize_evidence(documents)
    top_skills = evidence.get("top_skills", [])
    document_context = [
        {
            "id": document.get("id"),
            "title": document.get("title"),
            "type": document.get("type"),
            "skills": document.get("skills") or [],
            "summary": document.get("summary"),
            "verification_status": document.get("verification_status"),
        }
        for document in documents[:20]
    ]
    prompt = f"""You are an evidence-grounded career coach.
Use only the supplied portfolio evidence and clearly state uncertainty.
Do not predict hiring success, salary, or probability.

GOAL: {payload.goal}
TOP SKILL EVIDENCE: {top_skills}
DOCUMENTS: {document_context}
RECENT CONVERSATION: {payload.conversation_history[-4:]}

Return only JSON with:
- answer: concise grounded coaching summary
- roadmap: 3 to 5 actionable steps
- missing_skills: skills needed for the goal that are absent or weakly evidenced
- recommended_projects: exactly 2 project ideas that would create missing evidence
- evidence_used: document IDs actually used
- uncertainty: what cannot be concluded from the current portfolio
- evidence_basis: one of low, medium, high
"""
    try:
        result = await generate_json(prompt, temperature=0.15)
    except Exception:
        weak = [
            item["skill"] for item in top_skills
            if item.get("evidence_level") in {"Claimed", "Learned", "Certified"}
        ][:4]
        result = {
            "answer": "Build from your strongest demonstrated skills and add direct project or internship evidence for the target role.",
            "roadmap": [
                "Review the evidence currently connected to the target role.",
                "Build one focused project that demonstrates a weak or missing requirement.",
                "Add measurable outcomes and a public source link where possible.",
                "Practise explaining the evidence using problem, action, and result.",
            ],
            "missing_skills": weak,
            "recommended_projects": [
                "Create an end-to-end project using the strongest target-role skills.",
                "Create a smaller validation project for one weakly evidenced skill.",
            ],
            "evidence_used": [document.get("id") for document in documents[:4]],
            "uncertainty": "The AI service was unavailable, so deterministic evidence-based guidance is shown.",
            "evidence_basis": "medium" if documents else "low",
        }

    return _normalize_mentor_result(result, documents)


def _normalize_mentor_result(result: dict, documents: list[dict]) -> dict:
    owned_ids = {str(document.get("id")) for document in documents}
    evidence_used = [
        str(value) for value in (result.get("evidence_used") or [])
        if str(value) in owned_ids
    ]
    roadmap = [str(value).strip() for value in (result.get("roadmap") or []) if str(value).strip()][:5]
    projects = [str(value).strip() for value in (result.get("recommended_projects") or []) if str(value).strip()][:3]
    missing = [str(value).strip() for value in (result.get("missing_skills") or []) if str(value).strip()][:8]
    basis = str(result.get("evidence_basis") or "medium").lower()
    if basis not in {"low", "medium", "high"}:
        basis = "medium"
    return {
        "answer": str(result.get("answer") or "No grounded recommendation was generated."),
        "roadmap": roadmap,
        "missing_skills": missing,
        "recommended_projects": projects,
        "evidence_used": evidence_used,
        "uncertainty": str(result.get("uncertainty") or "Recommendations depend on the completeness and accuracy of uploaded evidence."),
        "evidence_basis": basis,
    }
