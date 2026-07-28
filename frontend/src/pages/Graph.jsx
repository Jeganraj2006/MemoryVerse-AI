import { useState, useEffect, useRef, useCallback } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { useLocation, useNavigate } from 'react-router-dom'
import * as d3 from 'd3'
import {
  Network, X, ExternalLink, Sparkles, RefreshCw, AlertTriangle, Trash2, Edit3, FileText, Copy, Check, Briefcase, Award, Zap, TrendingUp, Cpu, Loader
} from 'lucide-react'
import { getGraph, deleteDocument, generateResumeBullet, getCareerPath } from '../lib/api'
import TypeBadge from '../components/TypeBadge'
import EditModal from '../components/EditModal'

export default function Graph() {
  const location = useLocation()
  const navigate = useNavigate()
  const svgRef = useRef(null)
  
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [selectedNode, setSelectedNode] = useState(null)
  const [hoveredEdge, setHoveredEdge] = useState(null)
  const [activeSidebarTab, setActiveSidebarTab] = useState('details') // 'details' or 'career'

  // Edit modal state
  const [editModalOpen, setEditModalOpen] = useState(false)

  // ATS Resume Bullet State
  const [generatingBullet, setGeneratingBullet] = useState(false)
  const [resumeBullet, setResumeBullet] = useState('')
  const [copiedBullet, setCopiedBullet] = useState(false)

  // Career Suggestion State
  const [careerLoading, setCareerLoading] = useState(false)
  const [careerData, setCareerData] = useState(null)

  const fetchGraph = () => {
    setLoading(true)
    getGraph()
      .then(res => {
        setData(res)
        // Clear states
        setSelectedNode(null)
        setResumeBullet('')
      })
      .catch(console.error)
      .finally(() => setLoading(false))
  }

  useEffect(fetchGraph, [])

  const drawGraph = useCallback(() => {
    if (!data || !svgRef.current || !data.nodes.length) return

    const container = svgRef.current.parentElement
    const width = container.clientWidth
    const height = container.clientHeight || 580

    d3.select(svgRef.current).selectAll('*').remove()

    const svg = d3.select(svgRef.current)
      .attr('width', width)
      .attr('height', height)

    // Defs for glow filter
    const defs = svg.append('defs')
    const filter = defs.append('filter').attr('id', 'glow')
    filter.append('feGaussianBlur').attr('stdDeviation', 4).attr('result', 'coloredBlur')
    const merge = filter.append('feMerge')
    merge.append('feMergeNode').attr('in', 'coloredBlur')
    merge.append('feMergeNode').attr('in', 'SourceGraphic')

    // Arrow marker
    defs.append('marker')
      .attr('id', 'arrowhead')
      .attr('viewBox', '0 -5 10 10')
      .attr('refX', 20).attr('refY', 0)
      .attr('markerWidth', 6).attr('markerHeight', 6)
      .attr('orient', 'auto')
      .append('path')
      .attr('d', 'M0,-5L10,0L0,5')
      .attr('fill', '#475569')

    const g = svg.append('g')

    // Zoom & pan setup
    const zoomBehavior = d3.zoom()
      .scaleExtent([0.3, 3])
      .on('zoom', e => g.attr('transform', e.transform))
      
    svg.call(zoomBehavior)

    const simulation = d3.forceSimulation(data.nodes)
      .force('link', d3.forceLink(data.edges).id(d => d.id).distance(140))
      .force('charge', d3.forceManyBody().strength(-320))
      .force('center', d3.forceCenter(width / 2, height / 2))
      .force('collision', d3.forceCollide().radius(50))

    // Interactive wide lines for hover overlays
    const hoverLines = g.append('g')
      .selectAll('line')
      .data(data.edges)
      .join('line')
      .attr('stroke', 'transparent')
      .attr('stroke-width', 10)
      .style('cursor', 'pointer')
      .on('mouseenter', (e, d) => {
        setHoveredEdge({ edge: d, x: e.clientX, y: e.clientY })
        d3.select(`#edge-${d.id}`).attr('stroke-width', 3).attr('stroke-opacity', 0.9)
      })
      .on('mouseleave', (e, d) => {
        setHoveredEdge(null)
        d3.select(`#edge-${d.id}`).attr('stroke-width', 1.5).attr('stroke-opacity', 0.4)
      })

    // Visible edges
    const link = g.append('g')
      .selectAll('line')
      .data(data.edges)
      .join('line')
      .attr('id', d => `edge-${d.id}`)
      .attr('stroke', d => d.color ?? '#475569')
      .attr('stroke-opacity', 0.4)
      .attr('stroke-width', 1.5)
      .attr('marker-end', 'url(#arrowhead)')

    // Edge labels
    const edgeLabels = g.append('g')
      .selectAll('text')
      .data(data.edges)
      .join('text')
      .attr('text-anchor', 'middle')
      .attr('font-size', '9px')
      .attr('fill', '#475569')
      .attr('font-family', 'Inter, sans-serif')
      .text(d => d.label)

    // Nodes
    const node = g.append('g')
      .selectAll('g')
      .data(data.nodes)
      .join('g')
      .style('cursor', 'pointer')
      .call(d3.drag()
        .on('start', (e, d) => { if (!e.active) simulation.alphaTarget(0.3).restart(); d.fx = d.x; d.fy = d.y })
        .on('drag', (e, d) => { d.fx = e.x; d.fy = e.y })
        .on('end', (e, d) => { if (!e.active) simulation.alphaTarget(0); d.fx = null; d.fy = null })
      )
      .on('click', (e, d) => {
        e.stopPropagation()
        setSelectedNode(d)
        setResumeBullet('')
        setActiveSidebarTab('details')
      })

    // Node circle
    node.append('circle')
      .attr('r', 20)
      .attr('fill', d => `${d.color}22`)
      .attr('stroke', d => d.color)
      .attr('stroke-width', 1.5)
      .attr('filter', 'url(#glow)')

    // Node icon text (first letter of type)
    node.append('text')
      .attr('text-anchor', 'middle')
      .attr('dy', '0.35em')
      .attr('font-size', '11px')
      .attr('font-weight', '700')
      .attr('fill', d => d.color)
      .attr('font-family', 'Space Grotesk, sans-serif')
      .text(d => d.type?.[0] ?? '?')

    // Node label below
    node.append('text')
      .attr('text-anchor', 'middle')
      .attr('dy', '38px')
      .attr('font-size', '10px')
      .attr('fill', '#94a3b8')
      .attr('font-family', 'Inter, sans-serif')
      .text(d => d.label?.length > 20 ? d.label.slice(0, 18) + '…' : d.label)

    svg.on('click', () => setSelectedNode(null))

    simulation.on('tick', () => {
      link
        .attr('x1', d => d.source.x)
        .attr('y1', d => d.source.y)
        .attr('x2', d => d.target.x)
        .attr('y2', d => d.target.y)

      hoverLines
        .attr('x1', d => d.source.x)
        .attr('y1', d => d.source.y)
        .attr('x2', d => d.target.x)
        .attr('y2', d => d.target.y)

      edgeLabels
        .attr('x', d => ((d.source.x ?? 0) + (d.target.x ?? 0)) / 2)
        .attr('y', d => ((d.source.y ?? 0) + (d.target.y ?? 0)) / 2 - 6)

      node.attr('transform', d => `translate(${d.x},${d.y})`)
    })

    // Programmatic Zoom-Focus on URL search nodeId
    const queryParams = new URLSearchParams(location.search)
    const targetNodeId = queryParams.get('nodeId')
    if (targetNodeId) {
      setTimeout(() => {
        const target = data.nodes.find(n => n.id === targetNodeId)
        if (target) {
          setSelectedNode(target)
          svg.transition().duration(800).call(
            zoomBehavior.transform,
            d3.zoomIdentity.translate(width / 2 - target.x * 1.2, height / 2 - target.y * 1.2).scale(1.2)
          )
        }
      }, 500)
    }

  }, [data, location.search])

  useEffect(() => { drawGraph() }, [drawGraph])

  // Delete document handler
  const handleDeleteDoc = async () => {
    if (!selectedNode) return
    if (!window.confirm("Are you sure you want to delete this document? This will remove it from the database, delete its vector index, and clean up all graph relationships.")) return
    
    try {
      await deleteDocument(selectedNode.id)
      fetchGraph()
    } catch (err) {
      alert(`Delete failed: ${err.message}`)
    }
  }

  // Generate resume bullet point
  const handleGenerateBullet = async () => {
    if (!selectedNode || !data) return
    setGeneratingBullet(true)
    setResumeBullet('')
    setCopiedBullet(false)

    // Find all connected nodes
    const connectedNodeIds = data.edges
      .filter(e => e.source.id === selectedNode.id || e.target.id === selectedNode.id)
      .map(e => e.source.id === selectedNode.id ? e.target.id : e.source.id)
    
    const allClusterIds = [selectedNode.id, ...connectedNodeIds]

    try {
      const res = await generateResumeBullet(allClusterIds)
      setResumeBullet(res.bullet_point)
    } catch (err) {
      setResumeBullet(`Failed to generate bullet point: ${err.message}`)
    } finally {
      setGeneratingBullet(false)
    }
  }

  // Copy resume bullet to clipboard
  const handleCopyBullet = () => {
    if (!resumeBullet) return
    navigator.clipboard.writeText(resumeBullet)
    setCopiedBullet(true)
    setTimeout(() => setCopiedBullet(false), 2000)
  }

  // Career Guidance Generator
  const handleGenerateCareerPath = async () => {
    setCareerLoading(true)
    setCareerData(null)
    try {
      const res = await getCareerPath()
      setCareerData(res)
    } catch (err) {
      alert(`Failed to load suggestions: ${err.message}`)
    } finally {
      setCareerLoading(false)
    }
  }

  // Legend data
  const LEGEND = [
    { label: 'Certification', color: '#3b82f6' },
    { label: 'Project',       color: '#8b5cf6' },
    { label: 'Internship',    color: '#10b981' },
    { label: 'Achievement',   color: '#f59e0b' },
    { label: 'Academic',      color: '#ef4444' },
    { label: 'Skill',         color: '#ec4899' },
  ]

  return (
    <div>
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', marginBottom: 24 }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 8 }}>
            <Sparkles size={16} color="#f59e0b" />
            <span style={{ fontSize: '0.8rem', color: '#f59e0b', fontWeight: 600, letterSpacing: '0.06em' }}>CONNECTIONS</span>
          </div>
          <h1 className="heading-display" style={{ fontSize: '2rem', color: '#f1f5f9', marginBottom: 4 }}>
            Knowledge Graph
          </h1>
          <p style={{ color: '#94a3b8', fontSize: '0.9rem' }}>
            {data?.stats?.node_count ?? 0} documents · {data?.stats?.edge_count ?? 0} connections · Hover edges to explain links
          </p>
        </div>
        <div style={{ display: 'flex', gap: 10 }}>
          <button
            onClick={() => navigate('/share/portfolio')}
            className="btn-ghost"
            style={{ gap: 6, borderColor: 'rgba(16,185,129,0.3)', color: '#34d399' }}
          >
            <ExternalLink size={14} />
            Recruiter Link
          </button>
          <button onClick={fetchGraph} className="btn-ghost" style={{ gap: 6 }}>
            <RefreshCw size={14} />
            Refresh
          </button>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 340px', gap: 20 }}>
        {/* Graph canvas */}
        <div
          className="glass-card"
          style={{ height: 580, overflow: 'hidden', position: 'relative' }}
        >
          {loading ? (
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100%', color: '#64748b' }}>
              <div>
                <Network size={40} style={{ display: 'block', margin: '0 auto 12px', opacity: 0.3 }} />
                <div>Building your knowledge graph...</div>
              </div>
            </div>
          ) : !data?.nodes?.length ? (
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100%', color: '#64748b', textAlign: 'center' }}>
              <div>
                <Network size={40} style={{ display: 'block', margin: '0 auto 12px', opacity: 0.3 }} />
                <div style={{ fontWeight: 500, marginBottom: 4 }}>No documents yet</div>
                <div style={{ fontSize: '0.85rem' }}>Upload documents to see your knowledge graph.</div>
              </div>
            </div>
          ) : (
            <>
              <svg ref={svgRef} style={{ width: '100%', height: '100%' }} />

              {/* Edge Tooltip */}
              {hoveredEdge && (
                <div style={{
                  position: 'fixed',
                  left: hoveredEdge.x + 15,
                  top: hoveredEdge.y - 30,
                  background: '#0d1525',
                  border: '1px solid rgba(59, 130, 246, 0.3)',
                  borderRadius: 8,
                  padding: '8px 12px',
                  boxShadow: '0 4px 20px rgba(0,0,0,0.5)',
                  fontSize: '0.75rem',
                  zIndex: 200,
                  pointerEvents: 'none',
                  color: '#e2e8f0',
                  maxWidth: 240,
                }}>
                  <div style={{ fontWeight: 600, color: hoveredEdge.edge.color, marginBottom: 2 }}>
                    {hoveredEdge.edge.type}
                  </div>
                  <div>{hoveredEdge.edge.label}</div>
                  <div style={{ fontSize: '0.68rem', color: '#64748b', marginTop: 4 }}>
                    Confidence: {Math.round(hoveredEdge.edge.confidence * 100)}%
                  </div>
                </div>
              )}
            </>
          )}
        </div>

        {/* Sidebar panels */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
          
          {/* Tabs Selector for sidebar */}
          <div style={{ display: 'flex', background: 'rgba(17,24,39,0.5)', borderRadius: 10, padding: 3 }}>
            <button
              onClick={() => setActiveSidebarTab('details')}
              style={{
                flex: 1, padding: '6px 12px', borderRadius: 8, fontSize: '0.78rem', fontWeight: 600,
                background: activeSidebarTab === 'details' ? 'rgba(59,130,246,0.12)' : 'none',
                color: activeSidebarTab === 'details' ? '#60a5fa' : '#64748b',
                border: 'none', cursor: 'pointer', transition: 'all 0.2s'
              }}
            >
              Node Details
            </button>
            <button
              onClick={() => {
                setActiveSidebarTab('career')
                if (!careerData && !careerLoading) {
                  handleGenerateCareerPath()
                }
              }}
              style={{
                flex: 1, padding: '6px 12px', borderRadius: 8, fontSize: '0.78rem', fontWeight: 600,
                background: activeSidebarTab === 'career' ? 'rgba(59,130,246,0.12)' : 'none',
                color: activeSidebarTab === 'career' ? '#60a5fa' : '#64748b',
                border: 'none', cursor: 'pointer', transition: 'all 0.2s'
              }}
            >
              Career Advisor
            </button>
          </div>

          {activeSidebarTab === 'details' ? (
            <>
              {/* Selected node panel */}
              <AnimatePresence mode="wait">
                {selectedNode ? (
                  <motion.div
                    key={selectedNode.id}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: 10 }}
                    className="glass-card"
                    style={{ padding: '18px 20px', border: `1px solid ${selectedNode.color}33` }}
                  >
                    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 12 }}>
                      <TypeBadge type={selectedNode.type} size="sm" />
                      <button
                        onClick={() => setSelectedNode(null)}
                        style={{ background: 'none', border: 'none', cursor: 'pointer', color: '#64748b' }}
                      >
                        <X size={14} />
                      </button>
                    </div>
                    <div style={{ fontWeight: 700, fontSize: '0.95rem', color: '#e2e8f0', marginBottom: 6, lineHeight: 1.3 }}>
                      {selectedNode.label}
                    </div>
                    {selectedNode.date && (
                      <div style={{ fontSize: '0.75rem', color: '#64748b', marginBottom: 8 }}>{selectedNode.date}</div>
                    )}
                    {selectedNode.summary && (
                      <p style={{ fontSize: '0.78rem', color: '#94a3b8', lineHeight: 1.5, marginBottom: 12 }}>
                        {selectedNode.summary}
                      </p>
                    )}
                    {selectedNode.skills?.length > 0 && (
                      <div style={{ display: 'flex', flexWrap: 'wrap', gap: 4, marginBottom: 12 }}>
                        {selectedNode.skills.slice(0, 5).map(s => (
                          <span key={s} className="skill-tag">{s}</span>
                        ))}
                      </div>
                    )}

                    {/* ATS Bullet Generator Button Section */}
                    {selectedNode.node_kind !== 'skill' && <div style={{ borderTop: '1px solid rgba(148,163,184,0.08)', paddingTop: 12, marginBottom: 14 }}>
                      <div style={{ fontSize: '0.7rem', fontWeight: 600, color: '#64748b', marginBottom: 8, letterSpacing: '0.04em' }}>
                        RESUME BUILDER
                      </div>
                      {!resumeBullet && !generatingBullet && (
                        <button
                          onClick={handleGenerateBullet}
                          className="btn-ghost"
                          style={{ width: '100%', fontSize: '0.72rem', gap: 5, padding: '6px 12px', justifyContent: 'center' }}
                        >
                          <FileText size={12} />
                          Generate ATS Resume Bullet
                        </button>
                      )}
                      {generatingBullet && (
                        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 8, color: '#60a5fa', fontSize: '0.72rem', padding: '6px 0' }}>
                          <Loader size={12} style={{ animation: 'spin 1s linear infinite' }} />
                          Drafting ATS resume bullet...
                        </div>
                      )}
                      {resumeBullet && (
                        <div style={{ background: 'rgba(6,11,24,0.3)', border: '1px solid rgba(148,163,184,0.08)', borderRadius: 8, padding: 10, position: 'relative' }}>
                          <p style={{ fontSize: '0.72rem', color: '#cbd5e1', lineHeight: 1.4, paddingRight: 24 }}>
                            {resumeBullet}
                          </p>
                          <button
                            onClick={handleCopyBullet}
                            style={{
                              position: 'absolute', top: 6, right: 6,
                              background: 'none', border: 'none', cursor: 'pointer',
                              color: copiedBullet ? '#10b981' : '#64748b',
                            }}
                          >
                            {copiedBullet ? <Check size={12} /> : <Copy size={12} />}
                          </button>
                        </div>
                      )}
                    </div>}

                    {/* View, Edit, Delete Document controls */}
                    {selectedNode.node_kind !== 'skill' && <div style={{ display: 'flex', gap: 10, borderTop: '1px solid rgba(148,163,184,0.08)', paddingTop: 12 }}>
                      {selectedNode.file_url && (
                        <a
                          href={selectedNode.file_url}
                          target="_blank"
                          rel="noopener noreferrer"
                          style={{
                            flex: 1, textDecoration: 'none',
                          }}
                        >
                          <button className="btn-ghost" style={{ width: '100%', fontSize: '0.72rem', padding: '6px 0', justifyContent: 'center', gap: 4 }}>
                            <ExternalLink size={12} />
                            View File
                          </button>
                        </a>
                      )}
                      <button
                        onClick={() => setEditModalOpen(true)}
                        className="btn-ghost"
                        style={{ flex: 1, fontSize: '0.72rem', padding: '6px 0', justifyContent: 'center', gap: 4, color: '#fbbf24', borderColor: 'rgba(245,158,11,0.2)' }}
                      >
                        <Edit3 size={12} />
                        Edit
                      </button>
                      <button
                        onClick={handleDeleteDoc}
                        className="btn-ghost"
                        style={{ flex: 1, fontSize: '0.72rem', padding: '6px 0', justifyContent: 'center', gap: 4, color: '#f87171', borderColor: 'rgba(239,68,68,0.2)' }}
                      >
                        <Trash2 size={12} />
                        Delete
                      </button>
                    </div>}

                  </motion.div>
                ) : (
                  <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    className="glass-card"
                    style={{ padding: '16px 20px', color: '#64748b', fontSize: '0.78rem', textAlign: 'center' }}
                  >
                    Select any document node on the graph to display verified details, edit metadata, or generate ATS bullet points.
                  </motion.div>
                )}
              </AnimatePresence>

              {/* Legend details */}
              <div className="glass-card" style={{ padding: '16px 20px' }}>
                <div style={{ fontSize: '0.75rem', fontWeight: 600, color: '#64748b', marginBottom: 12, letterSpacing: '0.05em' }}>
                  NODE TYPES
                </div>
                {LEGEND.map(({ label, color }) => (
                  <div key={label} style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 8 }}>
                    <div style={{
                      width: 10, height: 10, borderRadius: '50%',
                      background: color,
                      boxShadow: `0 0 8px ${color}66`,
                    }} />
                    <span style={{ fontSize: '0.8rem', color: '#94a3b8' }}>{label}</span>
                  </div>
                ))}
              </div>

              {/* Relationship types details */}
              <div className="glass-card" style={{ padding: '16px 20px' }}>
                <div style={{ fontSize: '0.75rem', fontWeight: 600, color: '#64748b', marginBottom: 12, letterSpacing: '0.05em' }}>
                  RELATIONSHIP TYPES
                </div>
                {[
                  { type: 'EVIDENCES', desc: 'document supports a skill' },
                  { type: 'SUPPORTS_PROGRESSION_TO', desc: 'evidence-backed progression' },
                  { type: 'PART_OF', desc: 'same explicit program or organization' },
                  { type: 'PRECEDES', desc: 'chronological evidence link' },
                  { type: 'RELATED_TO', desc: 'shared factual evidence' },
                  { type: 'CONTRADICTS', desc: 'conflicting evidence requiring review' },
                ].map(r => (
                  <div key={r.type} style={{ marginBottom: 8 }}>
                    <div style={{ fontSize: '0.72rem', fontWeight: 600, color: '#60a5fa', marginBottom: 1 }}>{r.type}</div>
                    <div style={{ fontSize: '0.72rem', color: '#475569' }}>{r.desc}</div>
                  </div>
                ))}
              </div>
            </>
          ) : (
            /* Career Advisor Tab Panel */
            <div className="glass-card" style={{ padding: '18px 20px', minHeight: 280 }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginBottom: 14 }}>
                <Cpu size={14} color="#f59e0b" />
                <span style={{ fontSize: '0.8rem', fontWeight: 700, color: '#e2e8f0', fontFamily: 'Space Grotesk, sans-serif' }}>
                  AI Career Recommendations
                </span>
              </div>

              {careerLoading && (
                <div style={{ padding: '40px 0', textAlign: 'center', color: '#64748b', fontSize: '0.78rem' }}>
                  <Loader size={24} style={{ animation: 'spin 1.2s linear infinite', margin: '0 auto 10px', display: 'block' }} />
                  Analyzing your portfolio graph connections...
                </div>
              )}

              {!careerLoading && !careerData && (
                <div style={{ textAlign: 'center', padding: '20px 0' }}>
                  <button onClick={handleGenerateCareerPath} className="btn-primary" style={{ fontSize: '0.75rem', padding: '8px 16px' }}>
                    Generate Path
                  </button>
                </div>
              )}

              {!careerLoading && careerData && (
                <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
                  <div>
                    <div style={{ fontSize: '0.65rem', fontWeight: 600, color: '#64748b', marginBottom: 3, letterSpacing: '0.04em' }}>
                      RECOMMENDED DIRECTION
                    </div>
                    <div style={{ fontSize: '0.9rem', fontWeight: 700, color: '#fbbf24', display: 'flex', alignItems: 'center', gap: 5 }}>
                      <TrendingUp size={13} /> {careerData.career_title}
                    </div>
                  </div>

                  <div>
                    <div style={{ fontSize: '0.65rem', fontWeight: 600, color: '#64748b', marginBottom: 4, letterSpacing: '0.04em' }}>
                      RATIONALE
                    </div>
                    <p style={{ fontSize: '0.72rem', color: '#94a3b8', lineHeight: 1.4 }}>
                      {careerData.rationale}
                    </p>
                  </div>

                  {careerData.next_steps?.length > 0 && (
                    <div>
                      <div style={{ fontSize: '0.65rem', fontWeight: 600, color: '#64748b', marginBottom: 4, letterSpacing: '0.04em' }}>
                        NEXT MILESTONES
                      </div>
                      <div style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
                        {careerData.next_steps.map((step, i) => (
                          <div key={i} style={{ fontSize: '0.7rem', color: '#cbd5e1', display: 'flex', gap: 6 }}>
                            <span style={{ color: '#60a5fa' }}>•</span>
                            <span>{step}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {careerData.skills_to_acquire?.length > 0 && (
                    <div>
                      <div style={{ fontSize: '0.65rem', fontWeight: 600, color: '#64748b', marginBottom: 4, letterSpacing: '0.04em' }}>
                        SKILLS TO ACQUIRE
                      </div>
                      <div style={{ display: 'flex', flexWrap: 'wrap', gap: 4 }}>
                        {careerData.skills_to_acquire.map(skill => (
                          <span key={skill} className="skill-tag" style={{ fontSize: '0.65rem', padding: '0.1rem 0.4rem', borderColor: 'rgba(236,72,153,0.15)', color: '#f472b6', background: 'rgba(236,72,153,0.06)' }}>
                            {skill}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}

                  <button
                    onClick={handleGenerateCareerPath}
                    className="btn-ghost"
                    style={{ fontSize: '0.72rem', padding: '6px 0', width: '100%', justifyContent: 'center', marginTop: 8 }}
                  >
                    Recalculate Path
                  </button>
                </div>
              )}
            </div>
          )}

        </div>
      </div>

      {/* Edit modal */}
      <EditModal
        doc={selectedNode}
        isOpen={editModalOpen}
        onClose={() => {
          setEditModalOpen(false)
        }}
        onSave={() => {
          fetchGraph()
        }}
      />

      <style>{`
        @keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
      `}</style>
    </div>
  )
}
