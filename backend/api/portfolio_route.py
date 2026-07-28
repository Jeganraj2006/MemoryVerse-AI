from html import escape
from fastapi import APIRouter, Depends
from api.auth_middleware import get_current_user
from db.supabase_client import get_all_documents, store_portfolio_version
from services.evidence import summarize_evidence
router=APIRouter()
@router.get('/portfolio/generate')
async def generate(user_id:str=Depends(get_current_user)):
    docs=await get_all_documents(user_id=user_id); ev=summarize_evidence(docs)
    cards=''.join(f"<article><span>{escape(d['type'])}</span><h2>{escape(d['title'])}</h2><p>{escape(d.get('summary') or '')}</p><b>{escape(d.get('verification_status') or 'self_uploaded')}</b></article>" for d in docs)
    skills=''.join(f"<li>{escape(s['skill'])}: {s['evidence_level']} ({s['evidence_score']})</li>" for s in ev['top_skills'])
    html=f"<!doctype html><html><head><style>body{{font-family:Arial;background:#f6f8fc;color:#14213d;max-width:1000px;margin:auto;padding:40px}}article{{background:white;padding:20px;margin:15px 0;border-radius:14px;box-shadow:0 8px 25px #ccd3e0}}span{{text-transform:uppercase;font-size:12px}}</style></head><body><h1>Evidence-Backed Career Passport</h1><ul>{skills}</ul>{cards}</body></html>"
    rec=await store_portfolio_version({'html_code':html,'config':{'evidence_summary':ev}},user_id)
    return {'html_code':html,'version_id':rec.get('id'),'evidence_summary':ev}
