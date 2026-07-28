import { Outlet, NavLink, useLocation } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import {
  LayoutDashboard, Clock, Network, MessageSquare, Upload,
  Brain, Sparkles, Briefcase, FileText, Globe, GraduationCap, BarChart3, LogOut, ShieldCheck
} from 'lucide-react'
import { useAuth } from '../context/AuthContext'

const navItems = [
  { path: '/dashboard',           icon: LayoutDashboard, label: 'Dashboard' },
  { path: '/upload',              icon: Upload,          label: 'Upload' },
  { path: '/timeline',            icon: Clock,           label: 'Timeline' },
  { path: '/graph',               icon: Network,         label: 'Knowledge Graph' },
  { path: '/evidence',            icon: ShieldCheck,     label: 'Career Passport' },
  { path: '/chat',                icon: MessageSquare,   label: 'Ask AI' },
  { path: '/career-mentor',       icon: Briefcase,       label: 'Career Mentor' },
  { path: '/resume-builder',      icon: FileText,        label: 'Resume Builder' },
  { path: '/portfolio-generator', icon: Globe,           label: 'Portfolio Gen' },
  { path: '/interview-prep',      icon: GraduationCap,   label: 'Interview Prep' },
  { path: '/analytics',           icon: BarChart3,       label: 'Analytics' },
]

export default function Layout() {
  const location = useLocation()
  const { user, signOut } = useAuth()

  const initials = user?.user_metadata?.full_name
    ? user.user_metadata.full_name.split(' ').map(n => n[0]).join('').slice(0, 2).toUpperCase()
    : user?.email?.[0]?.toUpperCase() ?? 'U'

  const displayName = user?.user_metadata?.full_name || user?.email?.split('@')[0] || 'User'

  return (
    <div style={{ display: 'flex', minHeight: '100vh' }}>
      {/* Sidebar */}
      <aside style={{
        width: '240px',
        flexShrink: 0,
        background: 'rgba(13, 21, 37, 0.95)',
        borderRight: '1px solid rgba(148, 163, 184, 0.08)',
        display: 'flex',
        flexDirection: 'column',
        position: 'fixed',
        top: 0,
        left: 0,
        height: '100vh',
        zIndex: 100,
        backdropFilter: 'blur(20px)',
      }}>
        {/* Logo */}
        <div style={{ padding: '24px 20px', borderBottom: '1px solid rgba(148,163,184,0.08)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <div style={{
              width: 36, height: 36, borderRadius: 10,
              background: 'linear-gradient(135deg, #3b82f6, #8b5cf6)',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              boxShadow: '0 0 20px rgba(59,130,246,0.3)',
            }}>
              <Brain size={18} color="white" />
            </div>
            <div>
              <div style={{ fontFamily: 'Space Grotesk, sans-serif', fontWeight: 700, fontSize: '0.95rem', color: '#f1f5f9' }}>
                MemoryVerse
              </div>
              <div style={{ fontSize: '0.65rem', color: '#3b82f6', fontWeight: 600, letterSpacing: '0.05em' }}>
                EVIDENCE AI 3.0
              </div>
            </div>
          </div>
        </div>

        {/* Navigation */}
        <nav style={{ flex: 1, padding: '16px 12px', display: 'flex', flexDirection: 'column', gap: '4px', overflowY: 'auto' }}>
          {navItems.map(({ path, icon: Icon, label }) => (
            <NavLink
              key={path}
              to={path}
              style={({ isActive }) => ({
                display: 'flex',
                alignItems: 'center',
                gap: '10px',
                padding: '10px 12px',
                borderRadius: '10px',
                textDecoration: 'none',
                fontSize: '0.875rem',
                fontWeight: isActive ? 600 : 400,
                color: isActive ? '#f1f5f9' : '#64748b',
                background: isActive ? 'rgba(59, 130, 246, 0.12)' : 'transparent',
                border: isActive ? '1px solid rgba(59, 130, 246, 0.2)' : '1px solid transparent',
                transition: 'all 0.2s ease',
                position: 'relative',
              })}
            >
              {({ isActive }) => (
                <>
                  {isActive && (
                    <motion.div
                      layoutId="nav-indicator"
                      style={{
                        position: 'absolute',
                        left: 0, top: '50%',
                        transform: 'translateY(-50%)',
                        width: 3, height: 20,
                        background: 'linear-gradient(180deg, #3b82f6, #8b5cf6)',
                        borderRadius: '0 2px 2px 0',
                      }}
                      transition={{ type: 'spring', stiffness: 380, damping: 30 }}
                    />
                  )}
                  <Icon size={17} color={isActive ? '#60a5fa' : '#64748b'} />
                  <span>{label}</span>
                  {label === 'Career Mentor' && (
                    <Sparkles size={11} style={{ marginLeft: 'auto', color: '#f59e0b' }} />
                  )}
                </>
              )}
            </NavLink>
          ))}
        </nav>

        {/* User Profile + Logout */}
        <div style={{ padding: '12px', borderTop: '1px solid rgba(148,163,184,0.08)' }}>
          <div style={{
            display: 'flex', alignItems: 'center', gap: 10,
            padding: '10px 12px',
            borderRadius: 10,
            background: 'rgba(255,255,255,0.03)',
            border: '1px solid rgba(148,163,184,0.08)',
          }}>
            {/* Avatar */}
            <div style={{
              width: 34, height: 34, borderRadius: 10, flexShrink: 0,
              background: 'linear-gradient(135deg, #3b82f6, #8b5cf6)',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              fontFamily: 'Space Grotesk, sans-serif',
              fontWeight: 700, fontSize: '0.8rem', color: 'white',
            }}>
              {initials}
            </div>
            {/* Name + Email */}
            <div style={{ flex: 1, minWidth: 0 }}>
              <div style={{
                fontSize: '0.8rem', fontWeight: 600, color: '#e2e8f0',
                whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis',
              }}>{displayName}</div>
              <div style={{
                fontSize: '0.68rem', color: '#475569',
                whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis',
              }}>{user?.email}</div>
            </div>
            {/* Logout */}
            <button
              onClick={signOut}
              title="Sign out"
              style={{
                background: 'none', border: 'none', cursor: 'pointer',
                color: '#475569', padding: '4px', borderRadius: 6,
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                transition: 'color 0.2s, background 0.2s',
                flexShrink: 0,
              }}
              onMouseEnter={e => { e.currentTarget.style.color = '#ef4444'; e.currentTarget.style.background = 'rgba(239,68,68,0.1)' }}
              onMouseLeave={e => { e.currentTarget.style.color = '#475569'; e.currentTarget.style.background = 'none' }}
            >
              <LogOut size={15} />
            </button>
          </div>
        </div>
      </aside>

      {/* Main content */}
      <main style={{ flex: 1, marginLeft: '240px', minHeight: '100vh', overflowY: 'auto' }}>
        <AnimatePresence mode="wait">
          <motion.div
            key={location.pathname}
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -8 }}
            transition={{ duration: 0.2 }}
            style={{ padding: '32px 40px', minHeight: '100vh' }}
          >
            <Outlet />
          </motion.div>
        </AnimatePresence>
      </main>
    </div>
  )
}
