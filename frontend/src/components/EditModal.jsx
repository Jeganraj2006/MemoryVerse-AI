import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { X, Save, Sparkles } from 'lucide-react'
import { updateDocument } from '../lib/api'

export default function EditModal({ doc, isOpen, onClose, onSave }) {
  const [title, setTitle] = useState('')
  const [type, setType] = useState('Achievement')
  const [issuer, setIssuer] = useState('')
  const [date, setDate] = useState('')
  const [skills, setSkills] = useState('')
  const [summary, setSummary] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  useEffect(() => {
    if (doc) {
      setTitle(doc.title || '')
      setType(doc.type || 'Achievement')
      setIssuer(doc.issuer || '')
      setDate(doc.date || '')
      setSkills(Array.isArray(doc.skills) ? doc.skills.join(', ') : '')
      setSummary(doc.summary || '')
      setError(null)
    }
  }, [doc, isOpen])

  if (!isOpen || !doc) return null

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError(null)

    const skillList = skills
      .split(',')
      .map(s => s.trim())
      .filter(s => s.length > 0)

    const updates = {
      title,
      type,
      issuer: issuer || null,
      date: date || null,
      skills: skillList,
      summary: summary || null,
    }

    try {
      await updateDocument(doc.id, updates)
      onSave?.()
      onClose()
    } catch (err) {
      setError(err.message || 'Failed to update document.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <AnimatePresence>
      <div style={{
        position: 'fixed',
        inset: 0,
        backgroundColor: 'rgba(6, 11, 24, 0.75)',
        backdropFilter: 'blur(8px)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        zIndex: 1000,
        padding: 20,
      }}>
        <motion.div
          initial={{ opacity: 0, scale: 0.95, y: 15 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          exit={{ opacity: 0, scale: 0.95, y: 15 }}
          className="glass-card"
          style={{
            width: '100%',
            maxWidth: 550,
            padding: 28,
            maxHeight: '90vh',
            overflowY: 'auto',
            border: '1px solid rgba(59, 130, 246, 0.25)',
            boxShadow: '0 10px 30px rgba(0,0,0,0.5)',
          }}
        >
          {/* Header */}
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 20 }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
              <Sparkles size={16} color="#f59e0b" />
              <span style={{ fontSize: '1rem', fontWeight: 700, color: '#f1f5f9', fontFamily: 'Space Grotesk, sans-serif' }}>
                Correct Metadata
              </span>
            </div>
            <button
              onClick={onClose}
              style={{ background: 'none', border: 'none', cursor: 'pointer', color: '#64748b', padding: 4 }}
            >
              <X size={18} />
            </button>
          </div>

          {error && (
            <div style={{
              background: 'rgba(239,68,68,0.1)',
              border: '1px solid rgba(239,68,68,0.2)',
              borderRadius: 8,
              padding: '10px 14px',
              fontSize: '0.8rem',
              color: '#f87171',
              marginBottom: 16
            }}>
              {error}
            </div>
          )}

          {/* Form */}
          <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
            {/* Title */}
            <div>
              <label style={{ display: 'block', fontSize: '0.75rem', fontWeight: 600, color: '#64748b', marginBottom: 6, letterSpacing: '0.04em' }}>
                DOCUMENT TITLE
              </label>
              <input
                type="text"
                required
                value={title}
                onChange={e => setTitle(e.target.value)}
                style={{
                  width: '100%',
                  background: 'rgba(6, 11, 24, 0.4)',
                  border: '1px solid rgba(148,163,184,0.12)',
                  borderRadius: 8,
                  padding: '8px 12px',
                  fontSize: '0.85rem',
                  color: 'white',
                  outline: 'none',
                }}
              />
            </div>

            {/* Type & Date Row */}
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
              <div>
                <label style={{ display: 'block', fontSize: '0.75rem', fontWeight: 600, color: '#64748b', marginBottom: 6, letterSpacing: '0.04em' }}>
                  TYPE
                </label>
                <select
                  value={type}
                  onChange={e => setType(e.target.value)}
                  style={{
                    width: '100%',
                    background: 'rgba(6, 11, 24, 0.4)',
                    border: '1px solid rgba(148,163,184,0.12)',
                    borderRadius: 8,
                    padding: '8px 12px',
                    fontSize: '0.85rem',
                    color: 'white',
                    outline: 'none',
                  }}
                >
                  {['Certification', 'Project', 'Internship', 'Achievement', 'Academic', 'Skill'].map(t => (
                    <option key={t} value={t} style={{ background: '#0d1525', color: 'white' }}>{t}</option>
                  ))}
                </select>
              </div>

              <div>
                <label style={{ display: 'block', fontSize: '0.75rem', fontWeight: 600, color: '#64748b', marginBottom: 6, letterSpacing: '0.04em' }}>
                  DATE
                </label>
                <input
                  type="date"
                  value={date}
                  onChange={e => setDate(e.target.value)}
                  style={{
                    width: '100%',
                    background: 'rgba(6, 11, 24, 0.4)',
                    border: '1px solid rgba(148,163,184,0.12)',
                    borderRadius: 8,
                    padding: '8px 12px',
                    fontSize: '0.85rem',
                    color: 'white',
                    outline: 'none',
                  }}
                />
              </div>
            </div>

            {/* Issuer */}
            <div>
              <label style={{ display: 'block', fontSize: '0.75rem', fontWeight: 600, color: '#64748b', marginBottom: 6, letterSpacing: '0.04em' }}>
                ISSUER / INSTITUTION / SPONSOR
              </label>
              <input
                type="text"
                value={issuer}
                onChange={e => setIssuer(e.target.value)}
                style={{
                  width: '100%',
                  background: 'rgba(6, 11, 24, 0.4)',
                  border: '1px solid rgba(148,163,184,0.12)',
                  borderRadius: 8,
                  padding: '8px 12px',
                  fontSize: '0.85rem',
                  color: 'white',
                  outline: 'none',
                }}
              />
            </div>

            {/* Skills */}
            <div>
              <label style={{ display: 'block', fontSize: '0.75rem', fontWeight: 600, color: '#64748b', marginBottom: 6, letterSpacing: '0.04em' }}>
                DETECTED SKILLS (COMMA-SEPARATED)
              </label>
              <input
                type="text"
                value={skills}
                onChange={e => setSkills(e.target.value)}
                placeholder="Python, NLP, SQL..."
                style={{
                  width: '100%',
                  background: 'rgba(6, 11, 24, 0.4)',
                  border: '1px solid rgba(148,163,184,0.12)',
                  borderRadius: 8,
                  padding: '8px 12px',
                  fontSize: '0.85rem',
                  color: 'white',
                  outline: 'none',
                }}
              />
            </div>

            {/* Summary */}
            <div>
              <label style={{ display: 'block', fontSize: '0.75rem', fontWeight: 600, color: '#64748b', marginBottom: 6, letterSpacing: '0.04em' }}>
                SUMMARY / DESCRIPTION
              </label>
              <textarea
                rows={3}
                value={summary}
                onChange={e => setSummary(e.target.value)}
                style={{
                  width: '100%',
                  background: 'rgba(6, 11, 24, 0.4)',
                  border: '1px solid rgba(148,163,184,0.12)',
                  borderRadius: 8,
                  padding: '8px 12px',
                  fontSize: '0.85rem',
                  color: 'white',
                  outline: 'none',
                  resize: 'vertical',
                }}
              />
            </div>

            {/* Action Buttons */}
            <div style={{ display: 'flex', gap: 12, justifyContent: 'flex-end', marginTop: 10 }}>
              <button
                type="button"
                onClick={onClose}
                disabled={loading}
                className="btn-ghost"
                style={{ padding: '8px 16px', fontSize: '0.8rem' }}
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={loading}
                className="btn-primary"
                style={{ padding: '8px 16px', fontSize: '0.8rem', gap: 6 }}
              >
                <Save size={14} />
                {loading ? 'Saving...' : 'Save & Re-embed'}
              </button>
            </div>
          </form>
        </motion.div>
      </div>
    </AnimatePresence>
  )
}
