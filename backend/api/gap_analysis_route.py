"""Evidence-aware comparison of a job description and a student's portfolio."""
from __future__ import annotations

import re
from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from api.auth_middleware import get_current_user
from db.supabase_client import get_all_documents
from services.ai_client import generate_json
from services.evidence import build_skill_evidence
from services.review_gate import document_is_graph_eligible

router = APIRouter()


class GapRequest(BaseModel):
    job_description: str = Field(min_length=20, max_length=12000)


@router.post("/gap-analysis")
async def gap_analysis(payload: GapRequest, user_id: str = Depends(get_current_user)):
    documents = [doc for doc in await get_all_documents(user_id=user_id) if document_is_graph_eligible(doc)]
    skills = build_skill_evidence(documents)
    prompt = f"""Compare this job description with the student's evidence-backed skills.
A resume-only claim must not be treated as demonstrated evidence.

JOB DESCRIPTION:
{payload.job_description}

EVIDENCE:
{skills}

Return only JSON with:
- match_percentage: 0 to 100, based on explicit required skills only
- matching_skills
- missing_skills
- weak_evidence_skills
- learning_plan: 3 to 5 concrete actions
- evidence_notes: concise explanation of the scoring basis
"""
    try:
        result = await generate_json(prompt, temperature=0.0)
    except Exception:
        result = _keyword_fallback(payload.job_description, skills)
    return _normalize_gap_result(result, skills)


def _keyword_fallback(job_description: str, skills: list[dict]) -> dict:
    lowered = job_description.casefold()
    known = {item["skill"].casefold(): item for item in skills}
    matched = [item["skill"] for key, item in known.items() if _contains_term(lowered, key)]
    weak = [
        item["skill"] for item in skills
        if item["skill"] in matched and item.get("evidence_level") in {"Claimed", "Learned", "Certified"}
    ]
    # This fallback measures only portfolio skills explicitly named in the JD. It does
    # not pretend to infer every requirement from free text.
    named_portfolio_skills = [item for key, item in known.items() if _contains_term(lowered, key)]
    strong_matches = [item for item in named_portfolio_skills if item["skill"] not in weak]
    percentage = round(100 * len(strong_matches) / max(1, len(named_portfolio_skills)), 1) if named_portfolio_skills else 0
    return {
        "match_percentage": percentage,
        "matching_skills": matched,
        "missing_skills": [],
        "weak_evidence_skills": weak,
        "learning_plan": [
            "Add project or internship evidence for weak target-role skills.",
            "Upload or source-link evidence for requirements not yet represented.",
            "Add measurable outcomes to the strongest matching project.",
        ],
        "evidence_notes": "Fallback comparison used only portfolio skill names explicitly present in the job description; unrecognised requirements need AI or manual review.",
    }


def _contains_term(text: str, term: str) -> bool:
    return bool(re.search(rf"(?<![a-z0-9]){re.escape(term)}(?![a-z0-9])", text))


def _normalize_gap_result(result: dict, skills: list[dict]) -> dict:
    def clean_list(key: str, legacy_key: str | None = None, limit: int = 20) -> list[str]:
        values = result.get(key)
        if values is None and legacy_key:
            values = result.get(legacy_key)
        return [str(value).strip() for value in (values or []) if str(value).strip()][:limit]

    try:
        percentage = float(result.get("match_percentage", 0))
    except (TypeError, ValueError):
        percentage = 0
    return {
        "match_percentage": round(max(0, min(100, percentage)), 1),
        "matching_skills": clean_list("matching_skills", "matched_skills"),
        "missing_skills": clean_list("missing_skills"),
        "weak_evidence_skills": clean_list("weak_evidence_skills"),
        "learning_plan": clean_list("learning_plan", "recommendations", 8),
        "evidence_notes": str(result.get("evidence_notes") or "The comparison is based on the evidence currently stored in the career passport."),
        "portfolio_skill_count": len(skills),
        "methodology": "Evidence coverage comparison; not a hiring probability.",
    }
