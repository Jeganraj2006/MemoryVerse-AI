from fastapi import APIRouter, Depends
from api.auth_middleware import get_current_user
from db.supabase_client import get_all_documents, get_all_relationships, store_career_analysis
from services.ai_client import generate_json
from services.evidence import summarize_evidence
from services.review_gate import document_is_graph_eligible

router = APIRouter()

@router.get('/career-path')
async def career_path(user_id: str = Depends(get_current_user)):
    docs = [doc for doc in await get_all_documents(user_id=user_id) if document_is_graph_eligible(doc)]
    rels = await get_all_relationships(user_id)
    if not docs:
        return {'career_title':'Portfolio Empty','rationale':'Upload evidence to receive grounded guidance.','next_steps':['Upload and review your first document'],'recommended_projects':[],'skills_to_acquire':[],'evidence_used':[]}
    evidence = summarize_evidence(docs)
    prompt = f"""Act as a career researcher. Use only this portfolio evidence. Do not predict salary or success probability.
Documents: {[{k:d.get(k) for k in ('id','title','type','date','skills','technologies','summary')} for d in docs]}
Relationships: {rels}
Skill evidence: {evidence['top_skills']}
Return JSON with career_title, rationale, next_steps (3), recommended_projects (2), skills_to_acquire (3), evidence_used (document ids)."""
    try:
        result = await generate_json(prompt, temperature=0.1)
    except Exception:
        top = evidence['top_skills'][:3]
        result = {
            'career_title':'Evidence-Grounded Technology Professional',
            'rationale':'Your strongest evidence currently comes from ' + ', '.join(s['skill'] for s in top) + '. The recommendation is based on demonstrated and applied evidence rather than self-declared claims.',
            'next_steps':['Add one deeper project with measurable outcomes','Strengthen the weakest target-role skill','Verify certificates with issuer links where possible'],
            'recommended_projects':['Build an end-to-end project using your top evidenced skills','Create a project that addresses one identified skill gap'],
            'skills_to_acquire':[],
            'evidence_used':[d['id'] for d in docs[:5]],
        }
    await store_career_analysis({'analysis': result}, user_id)
    return result

@router.get('/career-path/scores')
async def career_scores(user_id: str = Depends(get_current_user)):
    """Backward-compatible route returning explainable evidence coverage, never job predictions."""
    docs = [doc for doc in await get_all_documents(user_id=user_id) if document_is_graph_eligible(doc)]
    evidence = summarize_evidence(docs)
    project_count = sum(d.get('type') == 'Project' for d in docs)
    internship_count = sum(d.get('type') == 'Internship' for d in docs)
    source_linked = sum(bool(d.get('source_url')) for d in docs)
    review_pending = sum(bool(d.get('review_required')) for d in docs)
    return {
        'document_count': len(docs),
        'project_evidence_count': project_count,
        'applied_evidence_count': internship_count,
        'source_linked_count': source_linked,
        'review_pending_count': review_pending,
        'reviewed_percentage': round(evidence['reviewed_ratio'] * 100),
        'top_skills': evidence['top_skills'][:5],
        'next_quality_actions': [
            'Review low-confidence metadata before sharing.',
            'Add measurable outcomes to project evidence.',
            'Link issuer or repository URLs to improve trust.',
        ],
        'methodology': 'Deterministic evidence counts and review coverage; no salary, hiring, or success prediction.',
    }
