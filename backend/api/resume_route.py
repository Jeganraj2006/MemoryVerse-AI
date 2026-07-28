from html import escape
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from api.auth_middleware import get_current_user
from db.supabase_client import get_all_documents, get_document_by_id, store_resume_version
from services.ai_client import generate_json, generate_text

router=APIRouter()
class BulletRequest(BaseModel): document_ids:list[str]=Field(min_length=1,max_length=10)
class ResumeRequest(BaseModel): resume_type:str='ATS'

@router.post('/generate-resume-bullet')
async def bullet(payload:BulletRequest,user_id:str=Depends(get_current_user)):
    docs=[await get_document_by_id(i,user_id) for i in payload.document_ids]; docs=[d for d in docs if d]
    if not docs: raise HTTPException(404,'No owned documents found.')
    prompt=f"Write one factual ATS resume bullet from this evidence. Do not invent metrics. Return only the sentence. Evidence: {docs}"
    try: text=await generate_text(prompt,temperature=0.1,max_output_tokens=220)
    except Exception: text=f"Built and documented {docs[0]['title']}, demonstrating {', '.join((docs[0].get('skills') or docs[0].get('technologies') or ['relevant technical skills'])[:3])}."
    return {'bullet_point':text.lstrip('-• ').strip(),'evidence_ids':[d['id'] for d in docs]}

@router.post('/resume/generate')
async def full_resume(payload:ResumeRequest,user_id:str=Depends(get_current_user)):
    docs=await get_all_documents(user_id=user_id)
    sections=''.join(f"<section><h2>{escape(d['title'])}</h2><p>{escape(d.get('summary') or '')}</p><small>{escape(', '.join(d.get('skills') or []))}</small></section>" for d in docs)
    html=f"<!doctype html><html><head><style>body{{font-family:Arial;max-width:820px;margin:40px auto;color:#172033}}h1{{border-bottom:2px solid #172033}}section{{margin:18px 0}}</style></head><body><h1>Evidence-Backed Resume</h1>{sections}</body></html>"
    latex='\\documentclass{article}\n\\begin{document}\n\\section*{Evidence-Backed Resume}\n'+ '\n'.join('\\subsection*{'+d['title'].replace('&','\\&')+'}\n'+(d.get('summary') or '') for d in docs)+'\n\\end{document}'
    record=await store_resume_version({'resume_type':payload.resume_type,'html_code':html,'latex_code':latex,'config':{'evidence_ids':[d['id'] for d in docs]}},user_id)
    return {'html_code':html,'latex_code':latex,'version_id':record.get('id'),'evidence_ids':[d['id'] for d in docs]}
