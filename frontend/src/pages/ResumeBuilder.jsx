import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  FileText, Sparkles, Download, Copy, Printer, Check, Plus, AlertCircle
} from 'lucide-react'
import { generateFullResume, generateResumeBullet, getCategories } from '../lib/api'

export default function ResumeBuilder() {
  const [resumeType, setResumeType] = useState('ATS')
  const [resumeData, setResumeData] = useState(null)
  const [loading, setLoading] = useState(false)
  const [copied, setCopied] = useState(false)
  const [activeSubTab, setActiveSubTab] = useState('preview') // 'preview' | 'latex' | 'config'

  // Bullet Point Optimizer state
  const [categories, setCategories] = useState(null)
  const [selectedDocIds, setSelectedDocIds] = useState([])
  const [bulletResult, setBulletResult] = useState('')
  const [bulletLoading, setBulletLoading] = useState(false)

  useEffect(() => {
    getCategories()
      .then(setCategories)
      .catch(console.error)
  }, [])

  const handleGenerateResume = async () => {
    setLoading(true)
    try {
      const res = await generateFullResume(resumeType)
      setResumeData(res)
    } catch (err) {
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  const handleCopyLaTeX = () => {
    if (!resumeData?.latex_code) return
    navigator.clipboard.writeText(resumeData.latex_code)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  const handleToggleDocSelect = (docId) => {
    setSelectedDocIds(prev =>
      prev.includes(docId) ? prev.filter(id => id !== docId) : [...prev, docId]
    )
  }

  const handleOptimizeBullet = async () => {
    if (selectedDocIds.length === 0 || bulletLoading) return
    setBulletLoading(true)
    try {
      const res = await generateResumeBullet(selectedDocIds)
      setBulletResult(res.bullet_point)
    } catch (err) {
      console.error(err)
    } finally {
      setBulletLoading(false)
    }
  }

  const allDocs = categories?.documents || []

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 24 }}>
      {/* Header */}
      <div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 8 }}>
          <FileText size={16} color="#8b5cf6" />
          <span style={{ fontSize: '0.8rem', color: '#8b5cf6', fontWeight: 600, letterSpacing: '0.06em' }}>
            RESUME GENERATION PORT
          </span>
        </div>
        <h1 className="heading-display" style={{ fontSize: '2rem', color: '#f1f5f9', marginBottom: 4 }}>
          AI Technical Resume Builder
        </h1>
        <p style={{ color: '#94a3b8', fontSize: '0.9rem' }}>
          Create ATS-optimized, Research, and Professional CV configurations. Export clean LaTeX or print direct PDF versions.
        </p>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1.2fr 1fr', gap: 20 }}>
        {/* Left Side: Customizer & Previews */}
        <div className="glass-card" style={{ padding: 24, display: 'flex', flexDirection: 'column', gap: 20 }}>
          <div style={{ display: 'flex', gap: 12, alignItems: 'center', justifyContent: 'space-between' }}>
            <h3 style={{ fontSize: '1rem', fontWeight: 700, color: '#f1f5f9' }}>Resume Type</h3>
            <div style={{ display: 'flex', gap: 8 }}>
              {['ATS', 'Research', 'Internship', 'Fresher', 'Experienced'].map(type => (
                <button
                  key={type}
                  className={resumeType === type ? 'btn-primary' : 'btn-ghost'}
                  onClick={() => setResumeType(type)}
                  style={{ padding: '6px 12px', fontSize: '0.8rem' }}
                >
                  {type}
                </button>
              ))}
            </div>
          </div>

          <button
            onClick={handleGenerateResume}
            disabled={loading}
            className="btn-primary"
            style={{ width: '100%', justifyContent: 'center', padding: 12, gap: 8 }}
          >
            <Sparkles size={16} />
            {loading ? 'Synthesizing Resume Draft…' : 'Generate Technical Resume'}
          </button>

          {/* Result view tabs */}
          {resumeData && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: 14, flex: 1 }}>
              <div style={{ display: 'flex', gap: 8, borderBottom: '1px solid rgba(148,163,184,0.08)', paddingBottom: 8 }}>
                <button
                  onClick={() => setActiveSubTab('preview')}
                  className={activeSubTab === 'preview' ? 'btn-primary' : 'btn-ghost'}
                  style={{ padding: '4px 10px', fontSize: '0.78rem' }}
                >
                  Letter Preview
                </button>
                <button
                  onClick={() => setActiveSubTab('latex')}
                  className={activeSubTab === 'latex' ? 'btn-primary' : 'btn-ghost'}
                  style={{ padding: '4px 10px', fontSize: '0.78rem' }}
                >
                  LaTeX Source
                </button>
              </div>

              <div style={{ flex: 1, minHeight: '380px', background: '#ffffff', borderRadius: 12, overflow: 'hidden', border: '1px solid rgba(148,163,184,0.1)' }}>
                {activeSubTab === 'preview' ? (
                  <iframe
                    srcDoc={resumeData.html_code}
                    title="Resume Preview"
                    style={{ width: '100%', height: '420px', border: 'none' }}
                  />
                ) : (
                  <div style={{ background: '#090d16', color: '#8ec07c', padding: 16, height: '420px', overflowY: 'auto', fontFamily: 'monospace', fontSize: '0.8rem', whiteSpace: 'pre-wrap', position: 'relative' }}>
                    <button
                      onClick={handleCopyLaTeX}
                      style={{ position: 'absolute', top: 12, right: 12, display: 'flex', gap: 4, alignItems: 'center', background: 'rgba(59,130,246,0.15)', border: '1px solid rgba(59,130,246,0.25)', color: '#60a5fa', padding: '4px 8px', borderRadius: 6, cursor: 'pointer', fontSize: '0.7rem' }}
                    >
                      {copied ? <Check size={12} color="#10b981" /> : <Copy size={12} />}
                      {copied ? 'Copied!' : 'Copy LaTeX'}
                    </button>
                    {resumeData.latex_code}
                  </div>
                )}
              </div>
            </div>
          )}
        </div>

        {/* Right Side: Bullet Point Optimizer */}
        <div className="glass-card" style={{ padding: 24, display: 'flex', flexDirection: 'column', gap: 16 }}>
          <h3 style={{ fontSize: '1rem', fontWeight: 700, color: '#f1f5f9', display: 'flex', alignItems: 'center', gap: 6 }}>
            <Sparkles size={16} color="#f59e0b" />
            Resume Bullet Point Optimizer
          </h3>
          <p style={{ fontSize: '0.78rem', color: '#64748b' }}>
            Select 1 or more documents representing a milestone cluster (e.g. Python cert + ML project), and we’ll draft a factual, action-oriented bullet point without inventing metrics.
          </p>

          {/* Doc selection checklist */}
          <div style={{
            flex: 1, maxHeight: '200px', overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: 6,
            background: 'rgba(6,11,24,0.4)', border: '1px solid rgba(148,163,184,0.06)', borderRadius: 10, padding: 12
          }}>
            {allDocs.length === 0 ? (
              <div style={{ color: '#475569', fontSize: '0.8rem', textAlign: 'center', margin: 'auto' }}>
                Upload documents to initialize optimizer lists.
              </div>
            ) : (
              allDocs.map(doc => (
                <label key={doc.id} style={{ display: 'flex', gap: 8, alignItems: 'center', cursor: 'pointer', padding: 4 }}>
                  <input
                    type="checkbox"
                    checked={selectedDocIds.includes(doc.id)}
                    onChange={() => handleToggleDocSelect(doc.id)}
                    style={{ accentColor: '#8b5cf6' }}
                  />
                  <span style={{ fontSize: '0.78rem', color: '#c7d2fe', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                    {doc.title} ({doc.type})
                  </span>
                </label>
              ))
            )}
          </div>

          <button
            onClick={handleOptimizeBullet}
            disabled={bulletLoading || selectedDocIds.length === 0}
            className="btn-primary"
            style={{ width: '100%', justifyContent: 'center', background: 'linear-gradient(135deg, #8b5cf6, #ec4899)' }}
          >
            {bulletLoading ? 'Synthesizing Resume Action Verb...' : 'Optimize Bullet Point'}
          </button>

          {bulletResult && (
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              style={{
                background: 'rgba(139,92,246,0.05)', border: '1px solid rgba(139,92,246,0.2)',
                borderRadius: 10, padding: 14, fontSize: '0.82rem', color: '#e2e8f0', lineHeight: 1.5,
                position: 'relative'
              }}
            >
              <div style={{ fontSize: '0.7rem', color: '#a78bfa', fontWeight: 700, marginBottom: 6 }}>
                EVIDENCE-GROUNDED BULLET POINT:
              </div>
              "{bulletResult}"
            </motion.div>
          )}
        </div>
      </div>
    </div>
  )
}
