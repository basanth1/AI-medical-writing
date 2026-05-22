import { useEffect } from 'react'
import { BrowserRouter, Routes, Route, Navigate, useNavigate } from 'react-router-dom'
import { Toaster } from 'react-hot-toast'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import Sidebar        from './components/layout/Sidebar.jsx'
import LoginPage      from './pages/LoginPage.jsx'
import GeneratePage   from './pages/GeneratePage.jsx'
import ReviewPage     from './pages/ReviewPage.jsx'
import FeedbackPage   from './pages/FeedbackPage.jsx'
import IngestPage     from './pages/IngestPage.jsx'
import CompliancePage from './pages/CompliancePage.jsx'
import AnalyticsPage  from './pages/AnalyticsPage.jsx'
import SettingsPage   from './pages/SettingsPage.jsx'
import FinalizedDocumentsPage from './pages/FinalizedDocumentsPage.jsx'
import { useAppStore } from './store/appStore.js'
import { apiService, API_ORIGIN }  from './services/api.js'

const queryClient = new QueryClient({ defaultOptions: { queries: { retry:1, staleTime:30_000 } } })

function AppShell() {
  const navigate = useNavigate()
  const {
    setServerStatus, setGroqAvailable, setVectorStats, initTheme,
    setOllamaAvailable, setOllamaModel, setGroqFallbackModel, setActiveGenerator,
  } = useAppStore()

  useEffect(() => {
    // Apply saved theme immediately on mount
    initTheme()

    const check = async () => {
      setServerStatus('checking')
      try {
        const data = await apiService.health()
        setServerStatus('online')
        setOllamaAvailable(data.ollama_available || false)
        setOllamaModel(data.ollama_model || '')
        setGroqAvailable(data.groq_available || false)
        setGroqFallbackModel(data.groq_fallback_model || '')
        setActiveGenerator(data.active_generator || 'template')
      } catch {
        setServerStatus('offline')
      }
    }
    apiService.checkAuth().then((session) => {
      if (session.role === 'admin') {
        window.location.assign(`${API_ORIGIN}/admin/ui`)
      }
    }).catch(() => navigate('/login', { replace: true }))
    check()
    apiService.getVectorStats().then(d => setVectorStats(d)).catch(() => {})
    const t = setInterval(check, 30_000)
    return () => clearInterval(t)
  }, [])

  return (
    <div style={{ display:'flex', height:'100vh', overflow:'hidden' }}>
      <Sidebar />
      <main style={{ flex:1, overflow:'hidden', display:'flex', flexDirection:'column' }}>
        <Routes>
          <Route path="/"            element={<GeneratePage />} />
          <Route path="/review"      element={<ReviewPage />} />
          <Route path="/feedback"    element={<FeedbackPage />} />
          <Route path="/ingest"      element={<IngestPage />} />
          <Route path="/compliance"  element={<CompliancePage />} />
          <Route path="/analytics"   element={<AnalyticsPage />} />
          <Route path="/finalized" element={<FinalizedDocumentsPage />} />
          <Route path="/settings"    element={<SettingsPage />} />
          <Route path="*"            element={<Navigate to="/" replace />} />
        </Routes>
      </main>
    </div>
  )
}

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route path="/*" element={<AppShell />} />
        </Routes>
        <Toaster position="bottom-right" toastOptions={{
          style: {
            background: 'var(--bg-elevated)', color: 'var(--text-primary)',
            border: '1px solid var(--border-soft)', fontSize: '13px', borderRadius: '10px',
          },
          success: { iconTheme: { primary: 'var(--success)', secondary: 'var(--bg-base)' } },
          error:   { iconTheme: { primary: 'var(--danger)',  secondary: 'var(--bg-base)' } },
        }} />
      </BrowserRouter>
    </QueryClientProvider>
  )
}
