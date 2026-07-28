import { useEffect, useState } from 'react'
import { Award, CheckCircle2, FileCheck2, ShieldCheck, AlertTriangle, ExternalLink } from 'lucide-react'
import { getSkillEvidence } from '../lib/api'

const levelHelp = {
  Claimed: 'Self-declared only', Learned: 'Academic evidence', Certified: 'Certificate evidence',
  Demonstrated: 'Project evidence', Recognized: 'Achievement evidence', Applied: 'Internship evidence',
  Verified: 'Externally verified evidence', Repeated: 'Repeated across independent sources',
}

export default function EvidencePassport(){
  const [data,setData]=useState(null); const [error,setError]=useState('')
  useEffect(()=>{getSkillEvidence().then(setData).catch(e=>setError(e.message))},[])
  if(error) return <div className="card" style={{padding:24,color:'#f87171'}}>{error}</div>
  if(!data) return <div style={{padding:40,color:'#94a3b8'}}>Building your evidence passport…</div>
  return <div style={{padding:'32px 36px',maxWidth:1200,margin:'0 auto'}}>
    <div style={{display:'flex',justifyContent:'space-between',gap:20,alignItems:'flex-start',marginBottom:24}}>
      <div><div className="eyebrow"><ShieldCheck size={14}/> TRUSTED CAREER IDENTITY</div><h1 className="heading-display" style={{fontSize:'2rem',margin:'6px 0'}}>Evidence-Backed Career Passport</h1><p style={{color:'#94a3b8',maxWidth:720}}>Every skill is separated into claimed, certified, demonstrated, applied, verified, or repeated evidence. Scores are explainable—not employment predictions.</p></div>
      <div className="card" style={{padding:'14px 18px',minWidth:190}}><b style={{fontSize:24}}>{data.skill_count}</b><div style={{color:'#64748b',fontSize:12}}>evidenced skills</div></div>
    </div>
    <div style={{display:'grid',gridTemplateColumns:'repeat(3,minmax(0,1fr))',gap:14,marginBottom:22}}>
      {[['Documents',data.document_count,FileCheck2],['Verified',data.verified_document_count,CheckCircle2],['Reviewed',`${Math.round(data.reviewed_ratio*100)}%`,AlertTriangle]].map(([label,value,Icon])=><div className="card" key={label} style={{padding:18,display:'flex',gap:12,alignItems:'center'}}><Icon size={20}/><div><b style={{fontSize:20}}>{value}</b><div style={{fontSize:12,color:'#64748b'}}>{label}</div></div></div>)}
    </div>
    <div style={{display:'grid',gap:14}}>{data.skills.map(skill=><section className="card" key={skill.skill} style={{padding:20}}>
      <div style={{display:'flex',justifyContent:'space-between',gap:16,alignItems:'center'}}><div><h2 style={{fontSize:17,margin:0}}>{skill.skill}</h2><div style={{fontSize:12,color:'#94a3b8',marginTop:4}}>{levelHelp[skill.evidence_level]} · {skill.evidence_count} source(s)</div></div><div style={{textAlign:'right'}}><b style={{fontSize:22}}>{skill.evidence_score}</b><div style={{fontSize:11,color:'#22d3ee'}}>{skill.evidence_level}</div></div></div>
      <div style={{height:7,background:'rgba(148,163,184,.12)',borderRadius:9,margin:'14px 0'}}><div style={{height:'100%',width:`${skill.evidence_score}%`,background:'linear-gradient(90deg,#3b82f6,#22d3ee)',borderRadius:9}}/></div>
      <div style={{display:'grid',gap:8}}>{skill.documents.map(doc=><div key={`${skill.skill}-${doc.document_id}`} style={{display:'flex',justifyContent:'space-between',gap:12,padding:'9px 11px',background:'rgba(15,23,42,.5)',borderRadius:9}}><div><b style={{fontSize:13}}>{doc.title}</b><div style={{fontSize:11,color:'#64748b'}}>{doc.type} · {doc.stage} · {doc.verification_status}</div></div>{doc.file_url&&<a href={doc.file_url} target="_blank" rel="noreferrer" style={{color:'#60a5fa'}}><ExternalLink size={15}/></a>}</div>)}</div>
    </section>)}</div>
  </div>
}
