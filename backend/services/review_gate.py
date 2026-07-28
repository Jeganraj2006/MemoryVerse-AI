"""Knowledge-integrity gate for AI-extracted documents."""
from __future__ import annotations
from core.config import get_settings

def review_decision(confidence: float | int | None, fields_needing_review: list[str] | None = None) -> dict:
    threshold = get_settings().review_confidence_threshold
    value = float(confidence or 0.0)
    fields = [str(item).strip() for item in (fields_needing_review or []) if str(item).strip()]
    held_out = value < threshold or bool(fields)
    reasons: list[str] = []
    if value < threshold:
        reasons.append(f"confidence {value:.0%} is below the {threshold:.0%} graph threshold")
    if fields:
        reasons.append(f"review required for: {', '.join(fields)}")
    return {"review_required": held_out, "graph_eligible": not held_out, "threshold": threshold, "reasons": reasons}

def document_is_graph_eligible(document: dict) -> bool:
    decision = review_decision(document.get("confidence"), document.get("fields_needing_review"))
    return decision["graph_eligible"] and not bool(document.get("review_required"))
