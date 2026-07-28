"""Transparent system and measured-fixture quality metrics."""
from __future__ import annotations
import json
from pathlib import Path
from fastapi import APIRouter, Depends
from api.auth_middleware import get_current_user
from core.config import get_settings
from db.supabase_client import get_all_documents, get_all_relationships
from embeddings.vector_store import get_collection_count
from services.evidence import summarize_evidence
from services.review_gate import document_is_graph_eligible
router=APIRouter(); RESULTS_DIR=Path(__file__).resolve().parents[1]/"evaluation"/"results"
def _read_result(filename):
    try:return json.loads((RESULTS_DIR/filename).read_text(encoding="utf-8"))
    except (OSError,json.JSONDecodeError):return None
@router.get("/evaluation/summary")
async def evaluation_summary(user_id:str=Depends(get_current_user)):
    docs=await get_all_documents(user_id=user_id); relationships=await get_all_relationships(user_id); evidence=summarize_evidence(docs); indexed=await get_collection_count(user_id)
    readable=sum(1 for d in docs if len((d.get("raw_text") or "").strip())>=40); cited=sum(1 for d in docs if d.get("page_count") and d.get("raw_text")); held=sum(1 for d in docs if not document_is_graph_eligible(d)); ocr=_read_result("ocr_benchmark_result.json"); offline=_read_result("offline_retrieval_result.json")
    return {"document_count":len(docs),"indexed_chunk_count":indexed,"relationship_count":len(relationships),"skill_count":evidence["skill_count"],"held_out_document_count":held,"graph_eligible_document_count":len(docs)-held,"review_confidence_threshold":get_settings().review_confidence_threshold,"readable_document_ratio":round(readable/len(docs),3) if docs else 0,"citation_ready_ratio":round(cited/len(docs),3) if docs else 0,"reviewed_ratio":evidence["reviewed_ratio"],"verified_ratio":evidence["verified_ratio"],"measured_fixture_metrics":{"ocr_key_field_recovery":ocr.get("ocr_key_field_recovery") if ocr else None,"ocr_fixture_count":ocr.get("fixture_count") if ocr else None,"offline_recall_at_5":offline.get("recall_at_5") if offline else None,"disclosure":"OCR uses 20 synthetically degraded scans. Offline Recall@5 uses TF-IDF over four synthetic demo documents and is not a Gemini embedding claim."},"disclaimer":"Coverage metrics describe this account. Included benchmark numbers are measured fixture results with explicit dataset disclosures, not production accuracy or hiring predictions."}
