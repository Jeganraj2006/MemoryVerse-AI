import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider } from './context/AuthContext'
import ProtectedRoute from './components/ProtectedRoute'
import Layout from './components/Layout'
import Login from './pages/Login'
import Dashboard from './pages/Dashboard'
import Timeline from './pages/Timeline'
import Graph from './pages/Graph'
import Chat from './pages/Chat'
import Upload from './pages/Upload'
import SharePortfolio from './pages/SharePortfolio'
import CareerMentor from './pages/CareerMentor'
import ResumeBuilder from './pages/ResumeBuilder'
import PortfolioGenerator from './pages/PortfolioGenerator'
import InterviewPrep from './pages/InterviewPrep'
import Analytics from './pages/Analytics'
import EvidencePassport from './pages/EvidencePassport'

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Routes>
          {/* Public routes */}
          <Route path="/login" element={<Login />} />
          <Route path="share/:id" element={<SharePortfolio />} />

          {/* Protected routes — require login */}
          <Route
            path="/"
            element={
              <ProtectedRoute>
                <Layout />
              </ProtectedRoute>
            }
          >
            <Route index element={<Navigate to="/dashboard" replace />} />
            <Route path="dashboard" element={<Dashboard />} />
            <Route path="timeline" element={<Timeline />} />
            <Route path="graph" element={<Graph />} />
            <Route path="evidence" element={<EvidencePassport />} />
            <Route path="chat" element={<Chat />} />
            <Route path="upload" element={<Upload />} />
            <Route path="career-mentor" element={<CareerMentor />} />
            <Route path="resume-builder" element={<ResumeBuilder />} />
            <Route path="portfolio-generator" element={<PortfolioGenerator />} />
            <Route path="interview-prep" element={<InterviewPrep />} />
            <Route path="analytics" element={<Analytics />} />
            <Route path="share/portfolio" element={<SharePortfolio />} />
          </Route>

          {/* Catch-all */}
          <Route path="*" element={<Navigate to="/dashboard" replace />} />
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  )
}
