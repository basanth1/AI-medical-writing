import axios from 'axios'

const API_BASE = import.meta.env.VITE_API_BASE || 'http://127.0.0.1:8765/api/v1'
const API_ORIGIN = new URL(API_BASE).origin

const api = axios.create({
  baseURL: API_BASE,
  timeout: 1000_000,
  withCredentials: true,
  headers: { 'Content-Type': 'application/json' },
})

const authApi = axios.create({
  baseURL: API_ORIGIN,
  timeout: 30_000,
  withCredentials: true,
  headers: { 'Content-Type': 'application/json' },
})

authApi.interceptors.response.use(
  (res) => res.data,
  (err) => {
    const msg = err.response?.data?.detail || err.message || 'Request failed'
    return Promise.reject(new Error(msg))
  }
)

// Response interceptor
api.interceptors.response.use(
  (res) => res.data,
  (err) => {
    const msg = err.response?.data?.detail || err.message || 'Request failed'
    return Promise.reject(new Error(msg))
  }
)

export const apiService = {
  // Health
  health: () => api.get('/health'),

  // Templates
  getTemplates: () => api.get('/templates'),
  getVectorStats: () => api.get('/vector-store'),

  // Ingest
  ingestDocument: (file, docType = 'historical_trial') => {
    const form = new FormData()
    form.append('file', file)
    return api.post(`/ingest/document?doc_type=${docType}`, form, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
  },
  ingestMetadata: (metadata) => api.post('/ingest/metadata', metadata),

  // Generate
  generateDocument: (payload) => api.post('/generate', payload),

  // Session
  getSession: (sessionId) => api.get(`/sessions/${sessionId}`),

  // Compliance
  runCompliance: (sessionId) => api.post(`/compliance/${sessionId}`),

  // Feedback
  submitFeedback: (sessionId, feedback) =>
    api.post(`/feedback/${sessionId}`, feedback),

  getPlaceholders:  (sessionId)           => api.get(`/placeholders/${sessionId}`),
  fillPlaceholders: (sessionId, replacements) =>
    api.post(`/placeholders/${sessionId}`, { replacements }),

  exportDocument: (sessionId, format) =>
  api.get(`/export/${sessionId}?format=${format}`, { responseType: 'blob' }),
  
  // Finalize
  // finalizeDocument: (sessionId) => api.post(`/finalize/${sessionId}`),
  listFinalizedDocuments: ()            => api.get('/finalized-documents'),
  getFinalizedDocument:   (sessionId)   => api.get(`/finalized-documents/${sessionId}`),
  deleteFinalizedDocument:(sessionId)   => api.delete(`/finalized-documents/${sessionId}`),
 
  // Updated finalize call (passes optional custom name)
  finalizeDocument: (sessionId, documentName) =>
    api.post(`/finalize/${sessionId}`, documentName ? { document_name: documentName } : {}),

  // Auth
  login: (credentials) => authApi.post('/auth/login', credentials),
  signup: (data) => authApi.post('/auth/signup', data),
  checkAuth: () => authApi.get('/auth/check'),
}

export { API_BASE, API_ORIGIN }
