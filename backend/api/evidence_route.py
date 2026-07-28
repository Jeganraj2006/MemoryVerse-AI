from fastapi import APIRouter, Depends
from api.auth_middleware import get_current_user
from db.supabase_client import get_all_documents
from services.evidence import summarize_evidence
from services.review_gate import document_is_graph_eligible

router = APIRouter()


@router.get("/evidence/skills")
async def skill_evidence(user_id: str = Depends(get_current_user)):
    documents = [doc for doc in await get_all_documents(user_id=user_id) if document_is_graph_eligible(doc)]
    return summarize_evidence(documents)
