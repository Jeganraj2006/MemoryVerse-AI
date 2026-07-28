import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  GraduationCap, Sparkles, Mic, MicOff, MessageSquare, Play, RefreshCw, CheckCircle, AlertTriangle
} from 'lucide-react'
import { generateInterviewQuestions, submitInterviewAnswers } from '../lib/api'

export default function InterviewPrep() {
  const [questions, setQuestions] = useState([])
  const [loading, setLoading] = useState(false)
  const [currentIndex, setCurrentIndex] = useState(-1) // -1 means welcome state
  const [answers, setAnswers] = useState({})
  
  // Voice states
  const [isRecording, setIsRecording] = useState(false)
  const [recognition, setRecognition] = useState(null)

  // Grading states
  const [submitting, setSubmitting] = useState(false)
  const [result, setResult] = useState(null)

  useEffect(() => {
    // Configure Web Speech API
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition
    if (SpeechRecognition) {
      const rec = new SpeechRecognition()
      rec.continuous = true
      rec.interimResults = false
      rec.lang = 'en-US'

      rec.onresult = (event) => {
        const text = event.results[event.results.length - 1][0].transcript
        setAnswers(prev => {
          const currentText = prev[currentIndex] || ''
          return {
            ...prev,
            [currentIndex]: currentText + ' ' + text
          }
        })
      }

      rec.onend = () => {
        setIsRecording(false)
      }

      setRecognition(rec)
    }
  }, [currentIndex])

  const handleStartInterview = async () => {
    setLoading(true)
    try {
      const res = await generateInterviewQuestions()
      setQuestions(res)
      setAnswers({})
      setResult(null)
      setCurrentIndex(0)
    } catch (err) {
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  const handleVoiceToggle = () => {
    if (!recognition) {
      alert("Speech recognition is not supported in this browser. Please type your answer.")
      return
    }
    if (isRecording) {
      recognition.stop()
    } else {
      setIsRecording(true)
      recognition.start()
    }
  }

  const handleNext = () => {
    if (currentIndex < questions.length - 1) {
      if (isRecording) {
        recognition.stop()
      }
      setCurrentIndex(prev => prev + 1)
    }
  }

  const handlePrev = () => {
    if (currentIndex > 0) {
      if (isRecording) {
        recognition.stop()
      }
      setCurrentIndex(prev => prev - 1)
    }
  }

  const handleSubmit = async () => {
    if (isRecording) {
      recognition.stop()
    }
    setSubmitting(true)
    try {
      const submissions = questions.map((q, idx) => ({
        question_id: q.id,
        question_text: q.text,
        question_type: q.type,
        user_answer: answers[idx] || "No answer provided."
      }))
      const res = await submitInterviewAnswers(submissions)
      setResult(res)
      setCurrentIndex(-1) // Return to results view
    } catch (err) {
      console.error(err)
    } finally {
      setSubmitting(false)
    }
  }

  const currentQuestion = questions[currentIndex]

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 24 }}>
      {/* Header */}
      <div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 8 }}>
          <GraduationCap size={16} color="#f59e0b" />
          <span style={{ fontSize: '0.8rem', color: '#f59e0b', fontWeight: 600, letterSpacing: '0.06em' }}>
            SIMULATION LAB
          </span>
        </div>
        <h1 className="heading-display" style={{ fontSize: '2rem', color: '#f1f5f9', marginBottom: 4 }}>
          AI Mock Interview & Voice Simulator
        </h1>
        <p style={{ color: '#94a3b8', fontSize: '0.9rem' }}>
          Interactive technical, behavioral HR, and system design interviews. Submit voice inputs and receive complete graded critiques.
        </p>
      </div>

      <div style={{ maxWidth: '800px', margin: '0 auto', width: '100%' }}>
        {/* Welcome State */}
        {currentIndex === -1 && !result && (
          <div className="glass-card" style={{ padding: 40, textAlign: 'center', display: 'flex', flexDirection: 'column', gap: 20 }}>
            <div style={{
              width: 60, height: 60, borderRadius: 16, background: 'rgba(245,158,11,0.1)',
              display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '0 auto'
            }}>
              <Play size={24} color="#f59e0b" />
            </div>
            <h2 style={{ fontSize: '1.25rem', fontWeight: 700 }}>Initialize Your Interview</h2>
            <p style={{ color: '#64748b', fontSize: '0.9rem', maxWidth: '460px', margin: '0 auto' }}>
              The AI will review your portfolio milestones and draft exactly 5 custom interview questions tailored to your skills and projects.
            </p>
            <button
              onClick={handleStartInterview}
              disabled={loading}
              className="btn-primary"
              style={{ margin: '12px auto 0', padding: '12px 30px', gap: 8 }}
            >
              <Sparkles size={16} />
              {loading ? 'Assembling Quiz Deck…' : 'Start Simulation'}
            </button>
          </div>
        )}

        {/* Question State */}
        {currentIndex >= 0 && currentQuestion && (
          <div className="glass-card" style={{ padding: 32, display: 'flex', flexDirection: 'column', gap: 20 }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <span style={{ fontSize: '0.78rem', color: '#64748b', fontWeight: 700 }}>
                QUESTION {currentIndex + 1} OF {questions.length}
              </span>
              <span style={{
                background: 'rgba(245,158,11,0.15)', color: '#fbbf24', border: '1px solid rgba(245,158,11,0.25)',
                padding: '4px 10px', borderRadius: 8, fontSize: '0.72rem', fontWeight: 700, textTransform: 'uppercase'
              }}>
                {currentQuestion.type}
              </span>
            </div>

            <div style={{ fontSize: '1.1rem', fontWeight: 600, color: '#f1f5f9', lineHeight: 1.5 }}>
              "{currentQuestion.text}"
            </div>

            {/* Answer text area */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span style={{ fontSize: '0.75rem', color: '#64748b' }}>TYPE OR SPEAK YOUR RESPONSE</span>
                <button
                  onClick={handleVoiceToggle}
                  style={{
                    display: 'flex', gap: 4, alignItems: 'center', background: isRecording ? 'rgba(239,68,68,0.15)' : 'rgba(59,130,246,0.15)',
                    border: isRecording ? '1px solid rgba(239,68,68,0.25)' : '1px solid rgba(59,130,246,0.25)',
                    color: isRecording ? '#ef4444' : '#60a5fa', padding: '6px 12px', borderRadius: 8, cursor: 'pointer',
                    fontSize: '0.75rem', fontWeight: 600
                  }}
                >
                  {isRecording ? <MicOff size={13} /> : <Mic size={13} />}
                  {isRecording ? 'Stop Recording' : 'Answer with Voice'}
                </button>
              </div>
              
              <textarea
                value={answers[currentIndex] || ''}
                onChange={e => setAnswers(prev => ({ ...prev, [currentIndex]: e.target.value }))}
                placeholder="Type your response here..."
                style={{
                  height: '140px', background: '#060b18', border: '1px solid rgba(148,163,184,0.15)',
                  borderRadius: 12, padding: 14, color: '#f1f5f9', fontSize: '0.85rem', outline: 'none',
                  resize: 'none', fontFamily: 'Inter, sans-serif'
                }}
              />
            </div>

            <div style={{ display: 'flex', justifyContent: 'space-between', borderTop: '1px solid rgba(148,163,184,0.08)', paddingTop: 16 }}>
              <button onClick={handlePrev} disabled={currentIndex === 0} className="btn-ghost" style={{ padding: '8px 16px', fontSize: '0.8rem' }}>
                Previous
              </button>
              
              <div style={{ display: 'flex', gap: 8 }}>
                {currentIndex < questions.length - 1 ? (
                  <button onClick={handleNext} className="btn-ghost" style={{ padding: '8px 16px', fontSize: '0.8rem' }}>
                    Next Question
                  </button>
                ) : (
                  <button onClick={handleSubmit} disabled={submitting} className="btn-primary" style={{ padding: '8px 20px', fontSize: '0.8rem' }}>
                    {submitting ? 'Analyzing Grades…' : 'Submit Interview'}
                  </button>
                )}
              </div>
            </div>
          </div>
        )}

        {/* Results State */}
        {result && (
          <motion.div
            initial={{ opacity: 0, y: 15 }}
            animate={{ opacity: 1, y: 0 }}
            className="glass-card"
            style={{ padding: 32, display: 'flex', flexDirection: 'column', gap: 24 }}
          >
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div>
                <h3 style={{ fontSize: '1.25rem', fontWeight: 800, color: '#f1f5f9' }}>Evaluation Scorecard</h3>
                <p style={{ fontSize: '0.78rem', color: '#64748b' }}>Evidence-aware coaching feedback — not a hiring prediction</p>
              </div>
              <div style={{
                width: 60, height: 60, borderRadius: '50%',
                background: `radial-gradient(closest-side, #0d1525 79%, transparent 80% 100%), conic-gradient(#f59e0b ${result.overall_score}%, rgba(148,163,184,0.08) 0)`,
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                fontSize: '1.1rem', fontWeight: 800, color: '#fbbf24'
              }}>
                {result.overall_score}%
              </div>
            </div>

            <div style={{ background: 'rgba(245,158,11,0.03)', border: '1px solid rgba(245,158,11,0.15)', borderRadius: 10, padding: 14, fontSize: '0.85rem', color: '#e2e8f0', lineHeight: 1.5 }}>
              <div style={{ fontSize: '0.75rem', color: '#fbbf24', fontWeight: 700, marginBottom: 4 }}>
                OVERALL FEEDBACK:
              </div>
              {result.feedback}
              {result.methodology && <div style={{ marginTop: 8, color: '#64748b', fontSize: '0.72rem' }}>{result.methodology}</div>}
            </div>

            {/* Detailed Question Review */}
            <div>
              <div style={{ fontSize: '0.8rem', color: '#64748b', fontWeight: 600, marginBottom: 12 }}>
                QUESTION BREAKDOWN
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
                {result.detailed_grades.map((grade, idx) => (
                  <div key={idx} style={{ background: 'rgba(148,163,184,0.01)', border: '1px solid rgba(148,163,184,0.05)', borderRadius: 10, padding: 16, display: 'flex', flexDirection: 'column', gap: 8 }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <span style={{ fontSize: '0.8rem', color: '#c7d2fe', fontWeight: 700 }}>Question {idx + 1}</span>
                      <span style={{ fontSize: '0.8rem', color: '#fbbf24', fontWeight: 700 }}>Score: {grade.score}%</span>
                    </div>
                    <div style={{ fontSize: '0.85rem', color: '#f1f5f9', fontWeight: 500 }}>"{grade.question_text}"</div>
                    
                    <div style={{ display: 'flex', flexDirection: 'column', gap: 6, borderTop: '1px solid rgba(148,163,184,0.06)', paddingTop: 10, marginTop: 4 }}>
                      <div style={{ fontSize: '0.75rem', color: '#ef4444', fontWeight: 600 }}>Critique:</div>
                      <div style={{ fontSize: '0.78rem', color: '#94a3b8', lineHeight: 1.4 }}>{grade.feedback}</div>
                      
                      <div style={{ fontSize: '0.75rem', color: '#10b981', fontWeight: 600, marginTop: 4 }}>Sample Ideal Answer:</div>
                      <div style={{ fontSize: '0.78rem', color: '#64748b', lineHeight: 1.4 }}>{grade.ideal_response}</div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <button
              onClick={handleStartInterview}
              className="btn-primary"
              style={{ width: '100%', justifyContent: 'center', padding: 12, gap: 8 }}
            >
              <RefreshCw size={14} />
              Restart Mock Interview Simulation
            </button>
          </motion.div>
        )}
      </div>
    </div>
  )
}
