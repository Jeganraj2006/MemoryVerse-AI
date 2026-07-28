import { useState } from 'react'
import { AlertTriangle, BookOpen, Briefcase, CheckCircle2, Compass, FileSearch, Sparkles, Target } from 'lucide-react'
import { runGapAnalysis, sendMentorMessage } from '../lib/api'

const ListCard = ({ title, icon: Icon, items = [], empty = 'No items identified.', accent = '#60a5fa' }) => (
  <section className="card" style={{ padding: 18, borderTop: `2px solid ${accent}` }}>
    <h3 style={{ display: 'flex', alignItems: 'center', gap: 7, fontSize: 14, margin: '0 0 12px' }}>
      <Icon size={15} style={{ color: accent }} /> {title}
    </h3>
    {items.length ? (
      <div style={{ display: 'grid', gap: 9 }}>
        {items.map((item, index) => (
          <div key={`${title}-${index}`} style={{ display: 'flex', gap: 9, color: '#cbd5e1', fontSize: 13, lineHeight: 1.5 }}>
            <span style={{ color: accent, fontWeight: 700 }}>{index + 1}.</span><span>{item}</span>
          </div>
        ))}
      </div>
    ) : <p style={{ color: '#64748b', fontSize: 13, margin: 0 }}>{empty}</p>}
  </section>
)

const CoverageRing = ({ value = 0 }) => {
  const safeValue = Math.max(0, Math.min(100, Number(value) || 0))
  return (
    <div
      aria-label={`${safeValue}% evidence coverage`}
      style={{
        width: 142,
        height: 142,
        borderRadius: '50%',
        display: 'grid',
        placeItems: 'center',
        flex: '0 0 auto',
        background: `conic-gradient(#22c55e ${safeValue * 3.6}deg, rgba(148,163,184,.13) 0deg)`,
        boxShadow: '0 0 34px rgba(34,197,94,.12)',
      }}
    >
      <div style={{ width: 108, height: 108, borderRadius: '50%', background: '#0b1424', display: 'grid', placeItems: 'center', textAlign: 'center' }}>
        <div><strong style={{ fontSize: 30 }}>{safeValue}%</strong><span style={{ display: 'block', color: '#64748b', fontSize: 11 }}>evidence coverage</span></div>
      </div>
    </div>
  )
}

const EvidenceLane = ({ label, count, total, accent }) => {
  const width = total ? Math.max(4, Math.round((count / total) * 100)) : 0
  return (
    <div style={{ display: 'grid', gap: 6 }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', color: '#94a3b8', fontSize: 12 }}><span>{label}</span><b style={{ color: accent }}>{count}</b></div>
      <div style={{ height: 7, borderRadius: 999, background: 'rgba(148,163,184,.11)', overflow: 'hidden' }}>
        <div style={{ width: `${width}%`, height: '100%', borderRadius: 999, background: accent }} />
      </div>
    </div>
  )
}

export default function CareerMentor() {
  const [activeTab, setActiveTab] = useState('coach')
  const [goal, setGoal] = useState('')
  const [mentorData, setMentorData] = useState(null)
  const [mentorLoading, setMentorLoading] = useState(false)
  const [jobDescription, setJobDescription] = useState('')
  const [gapData, setGapData] = useState(null)
  const [gapLoading, setGapLoading] = useState(false)
  const [error, setError] = useState('')

  const startCoaching = async () => {
    if (!goal.trim()) return
    setMentorLoading(true)
    setError('')
    try { setMentorData(await sendMentorMessage(goal, [])) }
    catch (err) { setError(err.message) }
    finally { setMentorLoading(false) }
  }

  const analyzeJob = async () => {
    if (jobDescription.trim().length < 20) return
    setGapLoading(true)
    setError('')
    try { setGapData(await runGapAnalysis(jobDescription)) }
    catch (err) { setError(err.message) }
    finally { setGapLoading(false) }
  }

  const totalRequirements = gapData
    ? gapData.matching_skills.length + gapData.missing_skills.length + gapData.weak_evidence_skills.length
    : 0

  return (
    <div style={{ display: 'grid', gap: 22 }}>
      <header>
        <div className="eyebrow"><Briefcase size={14} /> EVIDENCE-GROUNDED GUIDANCE</div>
        <h1 className="heading-display" style={{ fontSize: '2rem', margin: '7px 0' }}>Career Mentor & Role Gap Analysis</h1>
        <p style={{ color: '#94a3b8', maxWidth: 780 }}>
          Guidance is derived from your uploaded evidence. It does not predict salary, selection, or hiring probability.
        </p>
      </header>

      <div style={{ display: 'flex', gap: 10 }}>
        <button className={activeTab === 'coach' ? 'btn-primary' : 'btn-ghost'} onClick={() => setActiveTab('coach')}><Compass size={15} /> Goal Roadmap</button>
        <button className={activeTab === 'gap' ? 'btn-primary' : 'btn-ghost'} onClick={() => setActiveTab('gap')}><FileSearch size={15} /> Job Description</button>
      </div>

      {error && <div className="card" style={{ padding: 14, color: '#f87171' }}><AlertTriangle size={15} /> {error}</div>}

      {activeTab === 'coach' ? (
        <>
          <section className="card" style={{ padding: 22 }}>
            <label style={{ display: 'block', fontWeight: 700, marginBottom: 8 }}>Target role or goal</label>
            <p style={{ color: '#64748b', fontSize: 13, margin: '0 0 12px' }}>Example: “Become a data analyst intern using SQL, Power BI, and Python.”</p>
            <div style={{ display: 'flex', gap: 10, flexWrap: 'wrap' }}>
              <input value={goal} onChange={event => setGoal(event.target.value)} placeholder="Describe your target role" style={{ flex: '1 1 420px' }} />
              <button className="btn-primary" onClick={startCoaching} disabled={mentorLoading || !goal.trim()}><Sparkles size={15} /> {mentorLoading ? 'Building roadmap…' : 'Build grounded roadmap'}</button>
            </div>
          </section>

          {mentorData && (
            <div style={{ display: 'grid', gap: 14 }}>
              <section className="card" style={{ padding: 22 }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', gap: 16, alignItems: 'flex-start', flexWrap: 'wrap' }}>
                  <div><div className="eyebrow"><Target size={13} /> COACHING SUMMARY</div><p style={{ color: '#e2e8f0', lineHeight: 1.7, marginBottom: 0 }}>{mentorData.answer}</p></div>
                  <span style={{ border: '1px solid rgba(34,211,238,.28)', borderRadius: 999, padding: '6px 10px', color: '#67e8f9', fontSize: 12 }}>Evidence basis: {mentorData.evidence_basis}</span>
                </div>
              </section>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit,minmax(260px,1fr))', gap: 14 }}>
                <ListCard title="Action roadmap" icon={CheckCircle2} items={mentorData.roadmap} accent="#22c55e" />
                <ListCard title="Weak or missing evidence" icon={AlertTriangle} items={mentorData.missing_skills} empty="No specific gap was confidently identified." accent="#f59e0b" />
                <ListCard title="Projects that create proof" icon={BookOpen} items={mentorData.recommended_projects} accent="#60a5fa" />
              </div>
              <section className="card" style={{ padding: 16, color: '#94a3b8', fontSize: 13 }}><b style={{ color: '#cbd5e1' }}>Uncertainty:</b> {mentorData.uncertainty}</section>
            </div>
          )}
        </>
      ) : (
        <>
          <section className="card" style={{ padding: 22 }}>
            <label style={{ display: 'block', fontWeight: 700, marginBottom: 8 }}>Paste a job description</label>
            <textarea value={jobDescription} onChange={event => setJobDescription(event.target.value)} placeholder="Paste at least 20 characters…" style={{ width: '100%', minHeight: 220, resize: 'vertical' }} />
            <button className="btn-primary" onClick={analyzeJob} disabled={gapLoading || jobDescription.trim().length < 20} style={{ marginTop: 12 }}><FileSearch size={15} /> {gapLoading ? 'Comparing evidence…' : 'Compare with my evidence'}</button>
          </section>

          {gapData && (
            <div style={{ display: 'grid', gap: 14 }}>
              <section className="card" style={{ padding: 24, display: 'grid', gridTemplateColumns: 'repeat(auto-fit,minmax(230px,1fr))', gap: 26, alignItems: 'center' }}>
                <CoverageRing value={gapData.match_percentage} />
                <div>
                  <div className="eyebrow">TARGET ROLE PROOF MAP</div>
                  <h2 style={{ fontSize: 26, margin: '7px 0' }}>What is proven, weak, and missing</h2>
                  <p style={{ color: '#94a3b8', lineHeight: 1.65, margin: 0 }}>{gapData.evidence_notes}</p>
                  <p style={{ color: '#64748b', fontSize: 12, margin: '10px 0 0' }}>{gapData.methodology}</p>
                </div>
                <div style={{ display: 'grid', gap: 13 }}>
                  <EvidenceLane label="Strong matching evidence" count={gapData.matching_skills.length} total={totalRequirements} accent="#22c55e" />
                  <EvidenceLane label="Weak evidence" count={gapData.weak_evidence_skills.length} total={totalRequirements} accent="#f59e0b" />
                  <EvidenceLane label="Missing requirements" count={gapData.missing_skills.length} total={totalRequirements} accent="#f87171" />
                </div>
              </section>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit,minmax(240px,1fr))', gap: 14 }}>
                <ListCard title="Matching evidence" icon={CheckCircle2} items={gapData.matching_skills} accent="#22c55e" />
                <ListCard title="Missing requirements" icon={AlertTriangle} items={gapData.missing_skills} empty="No missing skill was confidently extracted." accent="#f87171" />
                <ListCard title="Weak evidence" icon={Target} items={gapData.weak_evidence_skills} empty="No weak evidence was identified." accent="#f59e0b" />
                <ListCard title="Learning and evidence plan" icon={BookOpen} items={gapData.learning_plan} accent="#60a5fa" />
              </div>
            </div>
          )}
        </>
      )}
    </div>
  )
}
