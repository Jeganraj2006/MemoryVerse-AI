"""Explainable document + skill knowledge graph."""
from __future__ import annotations

from fastapi import APIRouter, Depends

from api.auth_middleware import get_current_user
from db.supabase_client import get_all_documents, get_all_relationships
from services.evidence import build_skill_evidence
from services.review_gate import document_is_graph_eligible

router = APIRouter()

TYPE_COLORS = {
    "Certification": "#8b5cf6",
    "Project": "#3b82f6",
    "Internship": "#10b981",
    "Achievement": "#f59e0b",
    "Academic": "#ec4899",
    "Skill": "#64748b",
}


@router.get("/graph")
async def get_graph(focus_node_id: str | None = None, user_id: str = Depends(get_current_user)):
    documents = [doc for doc in await get_all_documents(user_id=user_id) if document_is_graph_eligible(doc)]
    relationships = await get_all_relationships(user_id)
    document_ids = {str(doc["id"]) for doc in documents}
    relationships = [rel for rel in relationships if str(rel.get("source_id")) in document_ids and str(rel.get("target_id")) in document_ids]
    skills = build_skill_evidence(documents)

    nodes = [{
        "id": str(doc["id"]),
        "node_kind": "document",
        "title": doc["title"],
        "label": doc["title"],
        "type": doc["type"],
        "date": doc.get("date"),
        "issuer": doc.get("issuer"),
        "skills": doc.get("skills") or [],
        "summary": doc.get("summary"),
        "file_url": doc.get("file_url"),
        "verification_status": doc.get("verification_status"),
        "review_required": doc.get("review_required", False),
        "color": TYPE_COLORS.get(doc["type"], "#64748b"),
        "radius": 24,
    } for doc in documents]

    edges = []
    for rel in relationships:
        edges.append({
            "id": str(rel["id"]),
            "source": str(rel["source_id"]),
            "target": str(rel["target_id"]),
            "relation_type": rel["relation_type"],
            "label": rel.get("label") or rel["relation_type"],
            "confidence": rel.get("confidence"),
            "evidence": rel.get("evidence") or {},
            "color": "#64748b",
        })

    for skill in skills:
        skill_id = f"skill:{skill['skill'].casefold()}"
        nodes.append({
            "id": skill_id,
            "node_kind": "skill",
            "title": skill["skill"],
            "label": skill["skill"],
            "type": "Skill Evidence",
            "evidence_level": skill["evidence_level"],
            "evidence_score": skill["evidence_score"],
            "color": "#22d3ee",
            "radius": 15 + min(12, skill["evidence_count"] * 2),
        })
        for evidence in skill["documents"]:
            edges.append({
                "id": f"{evidence['document_id']}:{skill_id}",
                "source": str(evidence["document_id"]),
                "target": skill_id,
                "relation_type": "EVIDENCES",
                "label": evidence["stage"],
                "confidence": min(1, skill["evidence_score"] / 100),
                "evidence": {"stage": evidence["stage"]},
                "color": "#22d3ee",
            })

    if focus_node_id:
        connected = {focus_node_id}
        for edge in edges:
            if edge["source"] == focus_node_id:
                connected.add(edge["target"])
            if edge["target"] == focus_node_id:
                connected.add(edge["source"])
        nodes = [node for node in nodes if node["id"] in connected]
        edges = [edge for edge in edges if edge["source"] in connected and edge["target"] in connected]

    return {
        "nodes": nodes,
        "edges": edges,
        "stats": {
            "node_count": len(nodes),
            "edge_count": len(edges),
            "document_count": len(documents),
            "skill_count": len(skills),
            "verified_count": sum(1 for doc in documents if doc.get("verification_status") == "verified"),
        },
    }
