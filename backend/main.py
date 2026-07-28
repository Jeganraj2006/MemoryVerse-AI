"""MemoryVerse AI — Evidence-Backed Career Passport API."""
from __future__ import annotations

from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from core.config import get_settings
from api.upload_route import router as upload_router
from api.source_route import router as source_router
from api.search_route import router as search_router
from api.chat_route import router as chat_router
from api.graph_route import router as graph_router
from api.timeline_route import router as timeline_router
from api.categories_route import router as categories_router
from api.documents_route import router as documents_router
from api.evidence_route import router as evidence_router
from api.evaluation_route import router as evaluation_router
from api.share_route import router as share_router
from api.career_route import router as career_router
from api.resume_route import router as resume_router
from api.mentor_route import router as mentor_router
from api.gap_analysis_route import router as gap_router
from api.portfolio_route import router as portfolio_router
from api.interview_route import router as interview_router

settings = get_settings()
app = FastAPI(
    title=settings.app_name,
    description="Private document intelligence, evidence graph, page-cited Graph-RAG, and source-linked career identity.",
    version="3.0.0",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=list(settings.allowed_origins),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

for router, tag in [
    (upload_router,"Ingestion"),(source_router,"Sources"),(search_router,"Search"),(chat_router,"Graph-RAG"),
    (graph_router,"Knowledge Graph"),(timeline_router,"Timeline"),(categories_router,"Documents"),
    (documents_router,"Documents"),(evidence_router,"Evidence Passport"),(evaluation_router,"Evaluation"),
    (share_router,"Sharing"),(career_router,"Career"),(resume_router,"Resume"),(mentor_router,"Mentor"),
    (gap_router,"Gap Analysis"),(portfolio_router,"Portfolio"),(interview_router,"Interview"),
]:
    app.include_router(router, prefix="/api", tags=[tag])

@app.get('/health')
async def health():
    return {
        'status':'ok','service':settings.app_name,'version':'3.0.0',
        'ai_configured':settings.ai_enabled,'supabase_configured':settings.supabase_enabled,
        'generation_model':settings.generation_model,'embedding_model':settings.embedding_model,
        'local_fallback_enabled':settings.allow_local_fallback,
    }
