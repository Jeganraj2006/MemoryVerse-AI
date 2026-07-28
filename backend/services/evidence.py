"""Deterministic, explainable skill-evidence scoring."""
from __future__ import annotations

from collections import defaultdict


TYPE_STAGE = {
    "Skill": ("Claimed", 1),
    "Certification": ("Certified", 2),
    "Academic": ("Learned", 2),
    "Project": ("Demonstrated", 3),
    "Achievement": ("Recognized", 3),
    "Internship": ("Applied", 4),
}

STAGE_SCORE = {
    "Claimed": 20,
    "Learned": 35,
    "Certified": 45,
    "Demonstrated": 65,
    "Recognized": 72,
    "Applied": 82,
    "Verified": 92,
    "Repeated": 100,
}


def build_skill_evidence(documents: list[dict]) -> list[dict]:
    grouped: dict[str, list[dict]] = defaultdict(list)
    display_names: dict[str, str] = {}

    for doc in documents:
        all_skills = list(doc.get("skills") or []) + list(doc.get("technologies") or [])
        seen = set()
        for skill in all_skills:
            label = str(skill).strip()
            key = label.casefold()
            if not label or key in seen:
                continue
            seen.add(key)
            display_names.setdefault(key, label)
            stage, rank = TYPE_STAGE.get(doc.get("type"), ("Claimed", 1))
            grouped[key].append({
                "document_id": doc.get("id"),
                "title": doc.get("title"),
                "type": doc.get("type"),
                "date": doc.get("date"),
                "stage": stage,
                "rank": rank,
                "verification_status": doc.get("verification_status", "self_uploaded"),
                "trust_level": doc.get("trust_level", "self_uploaded"),
                "file_url": doc.get("file_url"),
            })

    results = []
    for key, evidence in grouped.items():
        evidence.sort(key=lambda item: (item["rank"], item.get("date") or ""), reverse=True)
        stages = {item["stage"] for item in evidence}
        is_verified = any(item["verification_status"] == "verified" for item in evidence)
        independent_types = {item["type"] for item in evidence}

        if len(evidence) >= 3 and len(independent_types) >= 2:
            level = "Repeated"
        elif is_verified:
            level = "Verified"
        else:
            level = evidence[0]["stage"]

        base_score = STAGE_SCORE[level]
        breadth_bonus = min(8, max(0, len(independent_types) - 1) * 3)
        score = min(100, base_score + breadth_bonus)

        results.append({
            "skill": display_names[key],
            "evidence_level": level,
            "evidence_score": score,
            "evidence_count": len(evidence),
            "stages": sorted(stages),
            "documents": evidence,
            "explanation": _explain(level, evidence),
        })

    return sorted(results, key=lambda item: (-item["evidence_score"], item["skill"].casefold()))


def _explain(level: str, evidence: list[dict]) -> str:
    if level == "Repeated":
        return "Supported across multiple independent document types."
    if level == "Verified":
        return "At least one evidence source has been externally verified."
    if level == "Applied":
        return "Applied in internship or professional experience."
    if level == "Demonstrated":
        return "Demonstrated through project work."
    if level == "Certified":
        return "Supported by a certification."
    if level == "Learned":
        return "Supported by an academic record."
    return "Currently supported only by a self-declared skill source."


def summarize_evidence(documents: list[dict]) -> dict:
    skills = build_skill_evidence(documents)
    verified_docs = sum(1 for d in documents if d.get("verification_status") == "verified")
    reviewed_docs = sum(1 for d in documents if not d.get("review_required", False))
    return {
        "skills": skills,
        "top_skills": skills[:8],
        "skill_count": len(skills),
        "document_count": len(documents),
        "verified_document_count": verified_docs,
        "verified_ratio": round(verified_docs / len(documents), 3) if documents else 0,
        "reviewed_ratio": round(reviewed_docs / len(documents), 3) if documents else 0,
        "methodology": "Deterministic evidence hierarchy: claim < certification/academic < project < internship < verified/repeated evidence.",
    }
