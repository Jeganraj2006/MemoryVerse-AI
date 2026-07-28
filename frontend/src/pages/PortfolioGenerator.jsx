import { useState } from 'react'
import { motion } from 'framer-motion'
import {
  Globe, Sparkles, Download, Copy, Code, Check, Eye, HelpCircle
} from 'lucide-react'
import { generatePortfolio } from '../lib/api'

export default function PortfolioGenerator() {
  const [portfolioData, setPortfolioData] = useState(null)
  const [loading, setLoading] = useState(false)
  const [copied, setCopied] = useState(false)
  const [activeTab, setActiveTab] = useState('live') // 'live' | 'code'

  const handleGenerate = async () => {
    setLoading(true)
    try {
      const res = await generatePortfolio()
      setPortfolioData(res)
    } catch (err) {
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  const handleCopyCode = () => {
    if (!portfolioData?.html_code) return
    navigator.clipboard.writeText(portfolioData.html_code)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  const handleDownload = () => {
    if (!portfolioData?.html_code) return
    const blob = new Blob([portfolioData.html_code], { type: 'text/html' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = 'portfolio.html'
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 24 }}>
      {/* Header */}
      <div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 8 }}>
          <Globe size={16} color="#10b981" />
          <span style={{ fontSize: '0.8rem', color: '#10b981', fontWeight: 600, letterSpacing: '0.06em' }}>
            PORTFOLIO ENGINE
          </span>
        </div>
        <h1 className="heading-display" style={{ fontSize: '2rem', color: '#f1f5f9', marginBottom: 4 }}>
          AI Portfolio Website Generator
        </h1>
        <p style={{ color: '#94a3b8', fontSize: '0.9rem' }}>
          Assemble a premium glassmorphic portfolio site instantly from your verified documents. Ready to deploy or host on GitHub Pages.
        </p>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1.1fr 1fr', gap: 20 }}>
        {/* Left Side: Generator & Interactive Previews */}
        <div className="glass-card" style={{ padding: 24, display: 'flex', flexDirection: 'column', gap: 20 }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <h3 style={{ fontSize: '1rem', fontWeight: 700, color: '#f1f5f9' }}>Web Builder Controls</h3>
            {portfolioData && (
              <div style={{ display: 'flex', gap: 8 }}>
                <button
                  onClick={handleDownload}
                  style={{ display: 'flex', gap: 6, alignItems: 'center', background: 'rgba(16,185,129,0.12)', border: '1px solid rgba(16,185,129,0.25)', color: '#34d399', padding: '6px 12px', borderRadius: 8, cursor: 'pointer', fontSize: '0.78rem', fontWeight: 600 }}
                >
                  <Download size={14} />
                  Download HTML
                </button>
                <button
                  onClick={handleCopyCode}
                  style={{ display: 'flex', gap: 6, alignItems: 'center', background: 'rgba(59,130,246,0.12)', border: '1px solid rgba(59,130,246,0.25)', color: '#60a5fa', padding: '6px 12px', borderRadius: 8, cursor: 'pointer', fontSize: '0.78rem', fontWeight: 600 }}
                >
                  {copied ? <Check size={14} color="#10b981" /> : <Copy size={14} />}
                  {copied ? 'Copied!' : 'Copy Code'}
                </button>
              </div>
            )}
          </div>

          <button
            onClick={handleGenerate}
            disabled={loading}
            className="btn-primary"
            style={{ width: '100%', justifyContent: 'center', padding: 12, gap: 8 }}
          >
            <Sparkles size={16} />
            {loading ? 'Synthesizing Site Template…' : 'Compile Portfolio Website'}
          </button>

          {portfolioData && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
              <div style={{ display: 'flex', gap: 8, borderBottom: '1px solid rgba(148,163,184,0.08)', paddingBottom: 8 }}>
                <button
                  onClick={() => setActiveTab('live')}
                  className={activeTab === 'live' ? 'btn-primary' : 'btn-ghost'}
                  style={{ padding: '4px 10px', fontSize: '0.75rem' }}
                >
                  <Eye size={12} style={{ marginRight: 4 }} />
                  Live Preview
                </button>
                <button
                  onClick={() => setActiveTab('code')}
                  className={activeTab === 'code' ? 'btn-primary' : 'btn-ghost'}
                  style={{ padding: '4px 10px', fontSize: '0.75rem' }}
                >
                  <Code size={12} style={{ marginRight: 4 }} />
                  Source Code
                </button>
              </div>

              <div style={{ minHeight: '380px', background: '#0d1525', borderRadius: 12, overflow: 'hidden', border: '1px solid rgba(148,163,184,0.1)' }}>
                {activeTab === 'live' ? (
                  <iframe
                    srcDoc={portfolioData.html_code}
                    title="Portfolio Live Preview"
                    style={{ width: '100%', height: '420px', border: 'none', background: '#060b18' }}
                  />
                ) : (
                  <textarea
                    readOnly
                    value={portfolioData.html_code}
                    style={{
                      width: '100%', height: '420px', border: 'none', background: '#090d16',
                      color: '#a78bfa', padding: 16, fontFamily: 'monospace', fontSize: '0.8rem',
                      outline: 'none', resize: 'none'
                    }}
                  />
                )}
              </div>
            </div>
          )}
        </div>

        {/* Right Side: Architecture detail */}
        <div className="glass-card" style={{ padding: 24, display: 'flex', flexDirection: 'column', gap: 16 }}>
          <h3 style={{ fontSize: '1rem', fontWeight: 700, color: '#f1f5f9', display: 'flex', alignItems: 'center', gap: 6 }}>
            <HelpCircle size={16} color="#10b981" />
            Portfolio Deployment Guide
          </h3>
          <p style={{ fontSize: '0.8rem', color: '#94a3b8', lineHeight: 1.5 }}>
            The generated code is a fully static, self-contained single page. You can host this instantly:
          </p>

          <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
            <div style={{ background: 'rgba(148,163,184,0.02)', border: '1px solid rgba(148,163,184,0.06)', padding: 14, borderRadius: 10 }}>
              <div style={{ fontSize: '0.8rem', fontWeight: 700, color: '#e2e8f0', marginBottom: 4 }}>
                1. GitHub Pages (Free)
              </div>
              <div style={{ fontSize: '0.75rem', color: '#64748b', lineHeight: 1.4 }}>
                Create a repo named <code>username.github.io</code>, upload the downloaded <code>portfolio.html</code>, rename it to <code>index.html</code>, and commit it.
              </div>
            </div>

            <div style={{ background: 'rgba(148,163,184,0.02)', border: '1px solid rgba(148,163,184,0.06)', padding: 14, borderRadius: 10 }}>
              <div style={{ fontSize: '0.8rem', fontWeight: 700, color: '#e2e8f0', marginBottom: 4 }}>
                2. Vercel / Netlify Deploy
              </div>
              <div style={{ fontSize: '0.75rem', color: '#64748b', lineHeight: 1.4 }}>
                Drag and drop the folder containing <code>index.html</code> directly into Vercel/Netlify Dashboard for instant hosting.
              </div>
            </div>

            <div style={{ background: 'rgba(148,163,184,0.02)', border: '1px solid rgba(148,163,184,0.06)', padding: 14, borderRadius: 10 }}>
              <div style={{ fontSize: '0.8rem', fontWeight: 700, color: '#e2e8f0', marginBottom: 4 }}>
                3. Embedded Components
              </div>
              <div style={{ fontSize: '0.75rem', color: '#64748b', lineHeight: 1.4 }}>
                Includes interactive Javascript components for smooth scroll, glass hover glows, project tag searches, and contact models out of the box.
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
