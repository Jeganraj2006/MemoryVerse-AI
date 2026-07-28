import { Navigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { Brain } from 'lucide-react'

export default function ProtectedRoute({ children }) {
  const { user, loading } = useAuth()

  if (loading) {
    return (
      <div style={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        minHeight: '100vh',
        gap: '16px',
        background: 'var(--bg-base)',
      }}>
        <div style={{
          width: 52, height: 52, borderRadius: 14,
          background: 'linear-gradient(135deg, #3b82f6, #8b5cf6)',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          animation: 'pulse-glow 2s ease-in-out infinite',
          boxShadow: '0 0 30px rgba(59,130,246,0.4)',
        }}>
          <Brain size={26} color="white" />
        </div>
        <p style={{ color: 'var(--text-muted)', fontSize: '0.875rem', fontFamily: 'Inter, sans-serif' }}>
          Loading MemoryVerse…
        </p>
      </div>
    )
  }

  if (!user) {
    return <Navigate to="/login" replace />
  }

  return children
}
