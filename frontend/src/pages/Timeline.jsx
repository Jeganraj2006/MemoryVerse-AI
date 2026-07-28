import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { useNavigate } from 'react-router-dom'
import { Clock, Filter, ExternalLink, Calendar, Building2, Sparkles, Network } from 'lucide-react'
import { getTimeline, deleteDocument } from '../lib/api'
import TypeBadge from '../components/TypeBadge'
import EditModal from '../components/EditModal'

const TYPE_FILTERS = ['All', 'Certification', 'Project', 'Internship', 'Achievement', 'Academic', 'Skill']

const TYPE_DOT_COLORS = {
  Certification: '#3b82f6',
  Project:       '#8b5cf6',
  Internship:    '#10b981',
  Achievement:   '#f59e0b',
  Academic:      '#ef4444',
  Skill:         '#ec4899',
}

function TimelineEntry({ doc, index, onEdit, onDelete }) {
  const isLeft = index % 2 === 0
  const dotColor = TYPE_DOT_COLORS[doc.type] ?? '#64748b'

  return (
    <motion.div
      initial={{ opacity: 0, x: isLeft ? -30 : 30 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ delay: index * 0.06, duration: 0.4, ease: 'easeOut' }}
      style={{
        display: 'grid',
        gridTemplateColumns: '1fr 40px 1fr',
        alignItems: 'flex-start',
        marginBottom: 32,
        position: 'relative',
      }}
    >
      {/* Left card (even) or empty space (odd) */}
      <div style={{ paddingRight: 24, display: 'flex', justifyContent: 'flex-end' }}>
        {isLeft ? <TimelineCard doc={doc} dotColor={dotColor} align="right" onEdit={onEdit} onDelete={onDelete} /> : null}
      </div>

      {/* Center dot + line */}
      <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', zIndex: 2 }}>
        <motion.div
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
          transition={{ delay: index * 0.06 + 0.1, type: 'spring', stiffness: 400 }}
          style={{
            width: 16, height: 16, borderRadius: '50%',
            background: dotColor,
            border: '3px solid var(--bg-base)',
            boxShadow: `0 0 12px ${dotColor}66`,
            marginTop: 18,
          }}
        />
      </div>

      {/* Right card (odd) or empty space (even) */}
      <div style={{ paddingLeft: 24 }}>
        {!isLeft ? <TimelineCard doc={doc} dotColor={dotColor} align="left" onEdit={onEdit} onDelete={onDelete} /> : null}
      </div>
    </motion.div>
  )
}

function TimelineCard({ doc, dotColor, align, onEdit, onDelete }) {
  const navigate = useNavigate()

  return (
    <div
      className="glass-card"
      style={{
        padding: '16px 18px',
        maxWidth: 340,
        textAlign: align === 'right' ? 'right' : 'left',
        marginLeft: align === 'left' ? 0 : 'auto',
        width: '100%',
      }}
    >
      {/* Date */}
      {doc.date && (
        <div style={{ display: 'flex', alignItems: 'center', gap: 4, marginBottom: 8, justifyContent: align === 'right' ? 'flex-end' : 'flex-start' }}>
          <Calendar size={11} color="#64748b" />
          <span style={{ fontSize: '0.72rem', color: '#64748b', fontWeight: 500 }}>{doc.date}</span>
        </div>
      )}

      {/* Type badge */}
      <div style={{ marginBottom: 8, display: 'flex', justifyContent: align === 'right' ? 'flex-end' : 'flex-start' }}>
        <TypeBadge type={doc.type} size="sm" />
      </div>

      {/* Title */}
      <div style={{ fontWeight: 700, fontSize: '0.9rem', color: '#e2e8f0', marginBottom: 4, lineHeight: 1.3 }}>
        {doc.title}
      </div>

      {/* Issuer */}
      {doc.issuer && (
        <div style={{ display: 'flex', alignItems: 'center', gap: 4, marginBottom: 8, justifyContent: align === 'right' ? 'flex-end' : 'flex-start' }}>
          <Building2 size={11} color="#64748b" />
          <span style={{ fontSize: '0.75rem', color: '#64748b' }}>{doc.issuer}</span>
        </div>
      )}

      {/* Summary */}
      {doc.summary && (
        <div style={{ fontSize: '0.78rem', color: '#94a3b8', lineHeight: 1.5, marginBottom: 10 }}>
          {doc.summary}
        </div>
      )}

      {/* Skills */}
      {doc.skills?.length > 0 && (
        <div style={{
          display: 'flex', flexWrap: 'wrap', gap: 4,
          justifyContent: align === 'right' ? 'flex-end' : 'flex-start', marginBottom: 10
        }}>
          {doc.skills.slice(0, 4).map(s => (
            <span key={s} className="skill-tag">{s}</span>
          ))}
        </div>
      )}

      {/* Button controls row */}
      <div style={{
        display: 'flex',
        flexWrap: 'wrap',
        gap: 12,
        marginTop: 12,
        borderTop: '1px solid rgba(148,163,184,0.06)',
        paddingTop: 10,
        justifyContent: align === 'right' ? 'flex-end' : 'flex-start'
      }}>
        {doc.file_url && (
          <a
            href={doc.file_url}
            target="_blank"
            rel="noopener noreferrer"
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: 4,
              fontSize: '0.72rem',
              color: dotColor,
              textDecoration: 'none',
              fontWeight: 500,
            }}
          >
            <ExternalLink size={11} />
            View
          </a>
        )}
        <button
          onClick={() => navigate(`/graph?nodeId=${doc.id}`)}
          style={{
            background: 'none', border: 'none', cursor: 'pointer',
            display: 'inline-flex', alignItems: 'center', gap: 4,
            fontSize: '0.72rem', color: '#60a5fa', fontWeight: 500,
          }}
        >
          <Network size={11} />
          Graph
        </button>
        <button
          onClick={() => onEdit(doc)}
          style={{
            background: 'none', border: 'none', cursor: 'pointer',
            display: 'inline-flex', alignItems: 'center', gap: 4,
            fontSize: '0.72rem', color: '#f59e0b', fontWeight: 500,
          }}
        >
          Edit
        </button>
        <button
          onClick={() => onDelete(doc.id)}
          style={{
            background: 'none', border: 'none', cursor: 'pointer',
            display: 'inline-flex', alignItems: 'center', gap: 4,
            fontSize: '0.72rem', color: '#ef4444', fontWeight: 500,
          }}
        >
          Delete
        </button>
      </div>
    </div>
  )
}

export default function Timeline() {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [activeFilter, setActiveFilter] = useState('All')
  const [selectedDoc, setSelectedDoc] = useState(null)
  const [isModalOpen, setIsModalOpen] = useState(false)

  const fetchTimeline = () => {
    setLoading(true)
    getTimeline()
      .then(setData)
      .catch(console.error)
      .finally(() => setLoading(false))
  }

  useEffect(() => {
    fetchTimeline()
  }, [])

  const handleEdit = (doc) => {
    setSelectedDoc(doc)
    setIsModalOpen(true)
  }

  const handleDelete = async (docId) => {
    if (!window.confirm("Are you sure you want to delete this document? This will remove it from your portfolio, delete its vector index, and clean up all graph relationships.")) return
    try {
      await deleteDocument(docId)
      fetchTimeline()
    } catch (err) {
      alert(`Delete failed: ${err.message}`)
    }
  }

  const docs = data?.documents ?? []
  const filtered = activeFilter === 'All' ? docs : docs.filter(d => d.type === activeFilter)

  return (
    <div>
      {/* Header */}
      <div style={{ marginBottom: 32 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 8 }}>
          <Sparkles size={16} color="#f59e0b" />
          <span style={{ fontSize: '0.8rem', color: '#f59e0b', fontWeight: 600, letterSpacing: '0.06em' }}>JOURNEY</span>
        </div>
        <h1 className="heading-display" style={{ fontSize: '2rem', color: '#f1f5f9', marginBottom: 8 }}>
          Your Timeline
        </h1>
        <p style={{ color: '#94a3b8', fontSize: '0.95rem' }}>
          {docs.length} milestones, auto-arranged chronologically from your documents.
        </p>
      </div>

      {/* Filter bar */}
      <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap', marginBottom: 40 }}>
        {TYPE_FILTERS.map(f => (
          <button
            key={f}
            onClick={() => setActiveFilter(f)}
            style={{
              padding: '6px 16px', borderRadius: 999, fontSize: '0.8rem', fontWeight: 500,
              cursor: 'pointer', transition: 'all 0.2s',
              background: activeFilter === f ? 'linear-gradient(135deg, #3b82f6, #8b5cf6)' : 'rgba(17,24,39,0.6)',
              color: activeFilter === f ? 'white' : '#94a3b8',
              border: activeFilter === f ? 'none' : '1px solid rgba(148,163,184,0.1)',
              boxShadow: activeFilter === f ? '0 4px 15px rgba(59,130,246,0.3)' : 'none',
            }}
          >
            {f}
          </button>
        ))}
      </div>

      {/* Timeline */}
      {loading ? (
        <div style={{ textAlign: 'center', color: '#64748b', paddingTop: 60 }}>
          <Clock size={32} style={{ marginBottom: 12, opacity: 0.4 }} />
          <div>Loading your timeline...</div>
        </div>
      ) : filtered.length === 0 ? (
        <div style={{ textAlign: 'center', color: '#64748b', paddingTop: 60 }}>
          <Clock size={40} style={{ marginBottom: 12, opacity: 0.3 }} />
          <div style={{ fontSize: '1rem', fontWeight: 500, marginBottom: 4 }}>No entries yet</div>
          <div style={{ fontSize: '0.85rem' }}>Upload documents to populate your timeline.</div>
        </div>
      ) : (
        <div style={{ position: 'relative', paddingTop: 8 }}>
          {/* Center vertical line */}
          <div style={{
            position: 'absolute',
            left: '50%',
            top: 0, bottom: 0,
            width: 2,
            background: 'linear-gradient(180deg, rgba(59,130,246,0.4), rgba(139,92,246,0.4), rgba(59,130,246,0.1))',
            transform: 'translateX(-50%)',
          }} />

          {filtered.map((doc, i) => (
            <TimelineEntry key={doc.id} doc={doc} index={i} onEdit={handleEdit} onDelete={handleDelete} />
          ))}
        </div>
      )}

      {/* Shared Edit Modal */}
      <EditModal
        doc={selectedDoc}
        isOpen={isModalOpen}
        onClose={() => {
          setIsModalOpen(false)
          setSelectedDoc(null)
        }}
        onSave={() => {
          fetchTimeline()
        }}
      />
    </div>
  )
}
