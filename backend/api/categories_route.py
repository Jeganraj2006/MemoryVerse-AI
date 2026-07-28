from collections import Counter
from fastapi import APIRouter, Depends
from api.auth_middleware import get_current_user
from db.supabase_client import get_all_documents
from services.evidence import summarize_evidence

router = APIRouter()


@router.get("/categories")
async def get_categories(user_id: str = Depends(get_current_user)):
    docs = await get_all_documents(user_id=user_id)
    counts = Counter(doc.get("type") for doc in docs)
    return {
        "total": len(docs),
        "categories": [{"type": key, "count": counts.get(key, 0)} for key in ("Certification","Project","Internship","Achievement","Academic","Skill")],
        "documents": docs,
        "evidence_summary": summarize_evidence(docs),
    }
