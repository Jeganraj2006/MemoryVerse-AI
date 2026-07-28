from fastapi import APIRouter, Depends, Query
from api.auth_middleware import get_current_user
from db.supabase_client import get_all_documents

router = APIRouter()


@router.get("/timeline")
async def get_timeline(
    type: str | None = None,
    limit: int = Query(default=200, ge=1, le=500),
    user_id: str = Depends(get_current_user),
):
    docs = await get_all_documents(limit=limit, user_id=user_id)
    if type:
        docs = [doc for doc in docs if doc.get("type") == type]
    docs.sort(key=lambda doc: doc.get("date") or doc.get("created_at") or "")
    return {"count": len(docs), "timeline": docs, "documents": docs}
