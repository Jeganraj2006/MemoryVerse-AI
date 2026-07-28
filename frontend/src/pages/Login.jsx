import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import { Brain, Mail, Lock, Eye, EyeOff, Sparkles, ArrowRight, User, AlertCircle, CheckCircle2 } from 'lucide-react'
import { supabase } from '../lib/supabase'
import { useAuth } from '../context/AuthContext'

const GOOGLE_ICON = (
  <svg width="18" height="18" viewBox="0 0 48 48" fill="none" xmlns="http://www.w3.org/2000/svg">
    <path d="M47.5 24.5c0-1.6-.1-3.2-.4-4.7H24v8.9h13.2c-.6 3-2.3 5.5-4.9 7.2v6h7.9c4.6-4.2 7.3-10.5 7.3-17.4z" fill="#4285F4"/>
    <path d="M24 48c6.5 0 11.9-2.1 15.9-5.8l-7.9-6c-2.2 1.5-5 2.3-8 2.3-6.1 0-11.3-4.1-13.2-9.7H2.7v6.2C6.7 42.9 14.8 48 24 48z" fill="#34A853"/>
    <path d="M10.8 28.8A14.9 14.9 0 0 1 10 24c0-1.7.3-3.3.8-4.8v-6.2H2.7A23.9 23.9 0 0 0 0 24c0 3.9.9 7.5 2.7 10.7l8.1-5.9z" fill="#FBBC05"/>
    <path d="M24 9.5c3.4 0 6.5 1.2 8.9 3.5l6.7-6.7C35.9 2.5 30.4 0 24 0 14.8 0 6.7 5.1 2.7 12.7l8.1 6.2C12.7 13.6 17.9 9.5 24 9.5z" fill="#EA4335"/>
  </svg>
)

export default function Login() {
  const navigate = useNavigate()
  const { user } = useAuth()

  const [tab, setTab] = useState('signin') // 'signin' | 'signup'
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [fullName, setFullName] = useState('')
  const [showPass, setShowPass] = useState(false)
  const [loading, setLoading] = useState(false)
  const [googleLoading, setGoogleLoading] = useState(false)
  const [error, setError] = useState('')
  const [successMsg, setSuccessMsg] = useState('')

  // If already logged in, redirect to dashboard
  useEffect(() => {
    if (user) navigate('/dashboard', { replace: true })
  }, [user, navigate])

  const clearMessages = () => { setError(''); setSuccessMsg('') }

  const handleEmailAuth = async (e) => {
    e.preventDefault()
    clearMessages()
    setLoading(true)

    try {
      if (tab === 'signup') {
        const { error } = await supabase.auth.signUp({
          email,
          password,
          options: {
            data: { full_name: fullName },
          },
        })
        if (error) throw error
        setSuccessMsg('Account created! Check your email to confirm, then sign in.')
        setTab('signin')
      } else {
        const { error } = await supabase.auth.signInWithPassword({ email, password })
        if (error) throw error
        navigate('/dashboard', { replace: true })
      }
    } catch (err) {
      setError(err.message || 'Authentication failed. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  const handleGoogle = async () => {
    clearMessages()
    setGoogleLoading(true)
    try {
      const { error } = await supabase.auth.signInWithOAuth({
        provider: 'google',
        options: { redirectTo: `${window.location.origin}/dashboard` },
      })
      if (error) throw error
    } catch (err) {
      setError(err.message || 'Google sign-in failed.')
      setGoogleLoading(false)
    }
  }

  return (
    <div style={{
      minHeight: '100vh',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      padding: '24px',
      position: 'relative',
      overflow: 'hidden',
    }}>
      {/* Animated background orbs */}
      <div style={{
        position: 'fixed', inset: 0, zIndex: 0, pointerEvents: 'none',
        background: 'var(--bg-base)',
      }}>
        <div style={{
          position: 'absolute', width: 600, height: 600,
          borderRadius: '50%',
          background: 'radial-gradient(circle, rgba(59,130,246,0.12) 0%, transparent 70%)',
          top: '-20%', left: '-10%',
          animation: 'float1 8s ease-in-out infinite',
        }} />
        <div style={{
          position: 'absolute', width: 500, height: 500,
          borderRadius: '50%',
          background: 'radial-gradient(circle, rgba(139,92,246,0.10) 0%, transparent 70%)',
          bottom: '-15%', right: '-5%',
          animation: 'float2 10s ease-in-out infinite',
        }} />
        <div style={{
          position: 'absolute', width: 300, height: 300,
          borderRadius: '50%',
          background: 'radial-gradient(circle, rgba(16,185,129,0.07) 0%, transparent 70%)',
          top: '60%', left: '60%',
          animation: 'float1 12s ease-in-out infinite reverse',
        }} />
      </div>

      <style>{`
        @keyframes float1 {
          0%, 100% { transform: translate(0, 0) scale(1); }
          50% { transform: translate(30px, -30px) scale(1.05); }
        }
        @keyframes float2 {
          0%, 100% { transform: translate(0, 0) scale(1); }
          50% { transform: translate(-20px, 20px) scale(1.03); }
        }
        .auth-input {
          width: 100%;
          background: rgba(17, 24, 39, 0.8);
          border: 1px solid rgba(148, 163, 184, 0.12);
          border-radius: 10px;
          padding: 12px 44px 12px 44px;
          color: #f1f5f9;
          font-size: 0.9rem;
          font-family: 'Inter', sans-serif;
          outline: none;
          transition: border-color 0.2s, box-shadow 0.2s;
          box-sizing: border-box;
        }
        .auth-input:focus {
          border-color: rgba(59, 130, 246, 0.5);
          box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
        }
        .auth-input::placeholder { color: #475569; }
        .tab-btn {
          flex: 1;
          padding: 10px;
          border: none;
          background: transparent;
          font-family: 'Inter', sans-serif;
          font-size: 0.875rem;
          font-weight: 600;
          cursor: pointer;
          transition: color 0.2s;
          position: relative;
        }
      `}</style>

      {/* Login Card */}
      <motion.div
        initial={{ opacity: 0, y: 24, scale: 0.97 }}
        animate={{ opacity: 1, y: 0, scale: 1 }}
        transition={{ duration: 0.4, ease: 'easeOut' }}
        style={{
          position: 'relative', zIndex: 1,
          width: '100%', maxWidth: 440,
          background: 'rgba(13, 21, 37, 0.85)',
          backdropFilter: 'blur(24px)',
          border: '1px solid rgba(148, 163, 184, 0.1)',
          borderRadius: 20,
          overflow: 'hidden',
          boxShadow: '0 24px 64px rgba(0,0,0,0.5), 0 0 0 1px rgba(59,130,246,0.05)',
        }}
      >
        {/* Gradient top bar */}
        <div style={{
          height: 3,
          background: 'linear-gradient(90deg, #3b82f6, #8b5cf6, #10b981)',
        }} />

        <div style={{ padding: '36px 36px 32px' }}>
          {/* Logo */}
          <div style={{ textAlign: 'center', marginBottom: 28 }}>
            <div style={{ display: 'inline-flex', alignItems: 'center', gap: 10, marginBottom: 10 }}>
              <div style={{
                width: 44, height: 44, borderRadius: 12,
                background: 'linear-gradient(135deg, #3b82f6, #8b5cf6)',
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                boxShadow: '0 0 24px rgba(59,130,246,0.4)',
              }}>
                <Brain size={22} color="white" />
              </div>
              <div style={{ textAlign: 'left' }}>
                <div style={{
                  fontFamily: 'Space Grotesk, sans-serif',
                  fontWeight: 700, fontSize: '1.2rem', color: '#f1f5f9',
                }}>MemoryVerse</div>
                <div style={{ fontSize: '0.65rem', color: '#3b82f6', fontWeight: 600, letterSpacing: '0.08em' }}>
                  AI PORTFOLIO INTEL
                </div>
              </div>
            </div>
            <p style={{ color: '#64748b', fontSize: '0.85rem', lineHeight: 1.5 }}>
              Your personal AI career intelligence system
            </p>
          </div>

          {/* Tab Switcher */}
          <div style={{
            display: 'flex',
            background: 'rgba(255,255,255,0.04)',
            border: '1px solid rgba(148,163,184,0.1)',
            borderRadius: 10,
            padding: 4,
            marginBottom: 24,
            position: 'relative',
          }}>
            {['signin', 'signup'].map(t => (
              <button
                key={t}
                className="tab-btn"
                onClick={() => { setTab(t); clearMessages() }}
                style={{ color: tab === t ? '#f1f5f9' : '#64748b' }}
              >
                {t === 'signin' ? 'Sign In' : 'Create Account'}
              </button>
            ))}
            <motion.div
              layoutId="tab-pill"
              style={{
                position: 'absolute',
                top: 4, bottom: 4,
                width: 'calc(50% - 4px)',
                left: tab === 'signin' ? 4 : '50%',
                background: 'rgba(59,130,246,0.15)',
                border: '1px solid rgba(59,130,246,0.25)',
                borderRadius: 7,
                zIndex: 0,
              }}
              transition={{ type: 'spring', stiffness: 400, damping: 35 }}
            />
          </div>

          {/* Success Message */}
          <AnimatePresence>
            {successMsg && (
              <motion.div
                initial={{ opacity: 0, y: -8 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -8 }}
                style={{
                  display: 'flex', alignItems: 'flex-start', gap: 10,
                  background: 'rgba(16,185,129,0.1)',
                  border: '1px solid rgba(16,185,129,0.2)',
                  borderRadius: 10, padding: '12px 14px',
                  marginBottom: 16, color: '#34d399', fontSize: '0.84rem',
                }}
              >
                <CheckCircle2 size={16} style={{ flexShrink: 0, marginTop: 1 }} />
                {successMsg}
              </motion.div>
            )}
          </AnimatePresence>

          {/* Error Message */}
          <AnimatePresence>
            {error && (
              <motion.div
                initial={{ opacity: 0, y: -8 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -8 }}
                style={{
                  display: 'flex', alignItems: 'flex-start', gap: 10,
                  background: 'rgba(239,68,68,0.1)',
                  border: '1px solid rgba(239,68,68,0.2)',
                  borderRadius: 10, padding: '12px 14px',
                  marginBottom: 16, color: '#f87171', fontSize: '0.84rem',
                }}
              >
                <AlertCircle size={16} style={{ flexShrink: 0, marginTop: 1 }} />
                {error}
              </motion.div>
            )}
          </AnimatePresence>

          {/* Form */}
          <form onSubmit={handleEmailAuth} style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
            {/* Full Name (signup only) */}
            <AnimatePresence>
              {tab === 'signup' && (
                <motion.div
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: 'auto' }}
                  exit={{ opacity: 0, height: 0 }}
                  style={{ overflow: 'hidden', position: 'relative' }}
                >
                  <User size={16} style={{ position: 'absolute', left: 14, top: '50%', transform: 'translateY(-50%)', color: '#475569', zIndex: 1 }} />
                  <input
                    className="auth-input"
                    type="text"
                    placeholder="Full Name"
                    value={fullName}
                    onChange={e => setFullName(e.target.value)}
                    required={tab === 'signup'}
                    autoComplete="name"
                  />
                </motion.div>
              )}
            </AnimatePresence>

            {/* Email */}
            <div style={{ position: 'relative' }}>
              <Mail size={16} style={{ position: 'absolute', left: 14, top: '50%', transform: 'translateY(-50%)', color: '#475569', zIndex: 1 }} />
              <input
                className="auth-input"
                type="email"
                placeholder="Email address"
                value={email}
                onChange={e => setEmail(e.target.value)}
                required
                autoComplete="email"
              />
            </div>

            {/* Password */}
            <div style={{ position: 'relative' }}>
              <Lock size={16} style={{ position: 'absolute', left: 14, top: '50%', transform: 'translateY(-50%)', color: '#475569', zIndex: 1 }} />
              <input
                className="auth-input"
                type={showPass ? 'text' : 'password'}
                placeholder={tab === 'signup' ? 'Create password (min 6 chars)' : 'Password'}
                value={password}
                onChange={e => setPassword(e.target.value)}
                required
                minLength={tab === 'signup' ? 6 : undefined}
                autoComplete={tab === 'signup' ? 'new-password' : 'current-password'}
                style={{ paddingRight: 44 }}
              />
              <button
                type="button"
                onClick={() => setShowPass(v => !v)}
                style={{
                  position: 'absolute', right: 12, top: '50%',
                  transform: 'translateY(-50%)',
                  background: 'none', border: 'none', cursor: 'pointer',
                  color: '#475569', padding: 4,
                }}
              >
                {showPass ? <EyeOff size={16} /> : <Eye size={16} />}
              </button>
            </div>

            {/* Submit Button */}
            <motion.button
              type="submit"
              disabled={loading}
              whileHover={{ scale: loading ? 1 : 1.01 }}
              whileTap={{ scale: loading ? 1 : 0.98 }}
              style={{
                width: '100%',
                padding: '13px',
                background: loading
                  ? 'rgba(59,130,246,0.4)'
                  : 'linear-gradient(135deg, #3b82f6, #8b5cf6)',
                border: 'none',
                borderRadius: 10,
                color: 'white',
                fontWeight: 700,
                fontSize: '0.95rem',
                fontFamily: 'Inter, sans-serif',
                cursor: loading ? 'not-allowed' : 'pointer',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: 8,
                boxShadow: loading ? 'none' : '0 4px 20px rgba(59,130,246,0.35)',
                transition: 'all 0.2s',
                marginTop: 4,
              }}
            >
              {loading ? (
                <>
                  <div style={{
                    width: 18, height: 18, borderRadius: '50%',
                    border: '2px solid rgba(255,255,255,0.3)',
                    borderTopColor: 'white',
                    animation: 'spin 0.7s linear infinite',
                  }} />
                  <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
                  {tab === 'signup' ? 'Creating account…' : 'Signing in…'}
                </>
              ) : (
                <>
                  {tab === 'signup' ? (
                    <><Sparkles size={17} /> Create My Portfolio</>
                  ) : (
                    <>Sign In <ArrowRight size={17} /></>
                  )}
                </>
              )}
            </motion.button>
          </form>

          {/* Divider */}
          <div style={{
            display: 'flex', alignItems: 'center', gap: 12,
            margin: '20px 0',
          }}>
            <div style={{ flex: 1, height: 1, background: 'rgba(148,163,184,0.1)' }} />
            <span style={{ color: '#475569', fontSize: '0.78rem', fontWeight: 500 }}>or continue with</span>
            <div style={{ flex: 1, height: 1, background: 'rgba(148,163,184,0.1)' }} />
          </div>

          {/* Google OAuth */}
          <motion.button
            onClick={handleGoogle}
            disabled={googleLoading}
            whileHover={{ scale: googleLoading ? 1 : 1.01 }}
            whileTap={{ scale: googleLoading ? 1 : 0.98 }}
            style={{
              width: '100%',
              padding: '12px',
              background: 'rgba(255,255,255,0.05)',
              border: '1px solid rgba(148,163,184,0.15)',
              borderRadius: 10,
              color: '#e2e8f0',
              fontFamily: 'Inter, sans-serif',
              fontWeight: 600,
              fontSize: '0.9rem',
              cursor: googleLoading ? 'not-allowed' : 'pointer',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: 10,
              transition: 'all 0.2s',
              opacity: googleLoading ? 0.6 : 1,
            }}
          >
            {GOOGLE_ICON}
            {googleLoading ? 'Redirecting…' : 'Continue with Google'}
          </motion.button>

          {/* Footer note */}
          <p style={{
            textAlign: 'center',
            marginTop: 20,
            color: '#334155',
            fontSize: '0.75rem',
            lineHeight: 1.6,
          }}>
            By continuing, you agree to MemoryVerse AI's terms.
            <br />Your data is private and isolated to your account.
          </p>
        </div>
      </motion.div>
    </div>
  )
}
