import axios from 'axios'
import { supabase } from './supabase'

const backendBase = (import.meta.env.VITE_API_URL || '').replace(/\/$/, '')
const api = axios.create({ baseURL: `${backendBase}/api`, timeout: 90000 })
api.interceptors.request.use(async config => {
  const { data: { session } } = await supabase.auth.getSession()
  if (session?.access_token) config.headers.Authorization = `Bearer ${session.access_token}`
  return config
})
api.interceptors.response.use(r => r, error => Promise.reject(new Error(error.response?.data?.detail || error.message || 'Request failed')))

export const uploadDocument = async (file, onProgress) => {
  const formData = new FormData(); formData.append('file', file)
  return (await api.post('/upload', formData, { headers:{'Content-Type':'multipart/form-data'}, onUploadProgress:e=>onProgress?.(Math.round((e.loaded*100)/(e.total||e.loaded))) })).data
}
export const importGitHubRepository = async url => (await api.post('/sources/github',{url})).data
export const searchDocuments = async (query,type=null,limit=10) => (await api.get('/search',{params:{q:query,type:type||undefined,limit}})).data
export const sendChatMessage = async (question,conversationHistory=[]) => (await api.post('/chat',{question,conversation_history:conversationHistory})).data
export const getGraph = async focusNodeId => (await api.get('/graph',{params:{focus_node_id:focusNodeId||undefined}})).data
export const getTimeline = async type => (await api.get('/timeline',{params:{type:type||undefined}})).data
export const getCategories = async () => (await api.get('/categories')).data
export const updateDocument = async (id,updates) => (await api.put(`/documents/${id}`,updates)).data
export const deleteDocument = async id => (await api.delete(`/documents/${id}`)).data
export const seedPortfolio = async () => (await api.post('/seed-portfolio')).data
export const getSkillEvidence = async () => (await api.get('/evidence/skills')).data
export const getEvaluationSummary = async () => (await api.get('/evaluation/summary')).data
export const createPortfolioShare = async (documentIds=[],title='Evidence-Backed Career Passport',expiresAt=null) => (await api.post('/shares',{document_ids:documentIds,title,expires_at:expiresAt})).data
export const revokePortfolioShare = async token => (await api.delete(`/shares/${token}`)).data
export const getPublicShare = async token => (await axios.get(`${backendBase}/api/public/share/${token}`)).data
export const getCareerPath = async () => (await api.get('/career-path')).data
export const generateResumeBullet = async documentIds => (await api.post('/generate-resume-bullet',{document_ids:documentIds})).data
export const sendMentorMessage = async (goal,conversationHistory=[]) => (await api.post('/career-mentor/chat',{goal,conversation_history:conversationHistory})).data
export const runGapAnalysis = async jobDescription => (await api.post('/gap-analysis',{job_description:jobDescription})).data
export const generatePortfolio = async () => (await api.get('/portfolio/generate')).data
export const generateFullResume = async resumeType => (await api.post('/resume/generate',{resume_type:resumeType})).data
export const generateInterviewQuestions = async () => {
  const data = (await api.get('/interview/generate-questions')).data
  return (data.questions || []).map((item, index) => ({
    ...item,
    id: item.id ?? index + 1,
    text: item.text || item.question || 'Explain this portfolio evidence.',
    type: item.type || item.category || 'Evidence',
  }))
}
export const submitInterviewAnswers = async submissions => (await api.post('/interview/submit-answers',{submissions})).data
export default api
