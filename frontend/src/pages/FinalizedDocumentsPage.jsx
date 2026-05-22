// frontend/src/pages/FinalizedDocumentsPage.jsx
//
// Shows all finalized documents loaded from the backend on mount.
// Each card shows: document name, type, indication/phase, compliance score,
// feedback summary, word count, finalized date.
// Users can view full detail in a slide-over panel and export any format.

import { useState, useEffect, useCallback } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  Archive, CheckCircle, FileText, Trash2, Eye, ChevronDown,
  ChevronRight, Download, MessageSquare, AlertTriangle, BarChart2,
  Calendar, Hash, Loader, RefreshCw, X,
} from 'lucide-react'
import Topbar from '../components/layout/Topbar.jsx'
import ExportButton from '../components/document/ExportButton.jsx'
import { Badge, Button, Card } from '../components/ui/index.jsx'
import { apiService } from '../services/api.js'
import { useAppStore } from '../store/appStore.js'
import toast from 'react-hot-toast'

// ── Helpers ────────────────────────────────────────────────────────────────────

function fmtDate(iso) {
  if (!iso) return '—'
  try {
    return new Date(iso).toLocaleDateString('en-US', {
      year: 'numeric', month: 'short', day: 'numeric',
      hour: '2-digit', minute: '2-digit',
    })
  } catch { return iso }
}

function scoreColor(score) {
  if (score >= 80) return 'var(--success)'
  if (score >= 60) return 'var(--warning)'
  return 'var(--danger)'
}

function scoreLabel(score) {
  if (score >= 80) return 'Compliant'
  if (score >= 60) return 'Partial'
  return 'Non-compliant'
}

// ── Feedback breakdown mini-component ─────────────────────────────────────────

function FeedbackBreakdown({ feedbackLog = [] }) {
  const approved = feedbackLog.filter(f => f.action === 'approve').length
  const revised  = feedbackLog.filter(f => f.action === 'revise').length
  const rejected = feedbackLog.filter(f => f.action === 'reject').length

  if (!feedbackLog.length) {
    return <span style={{ fontSize: 11, color: 'var(--text-muted)' }}>No feedback recorded</span>
  }

  return (
    <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
      {approved > 0 && (
        <span style={{ fontSize: 11, color: 'var(--success)', display: 'flex', alignItems: 'center', gap: 3 }}>
          <CheckCircle size={10} /> {approved} approved
        </span>
      )}
      {revised > 0 && (
        <span style={{ fontSize: 11, color: 'var(--warning)', display: 'flex', alignItems: 'center', gap: 3 }}>
          ✏ {revised} revised
        </span>
      )}
      {rejected > 0 && (
        <span style={{ fontSize: 11, color: 'var(--danger)', display: 'flex', alignItems: 'center', gap: 3 }}>
          ✕ {rejected} rejected
        </span>
      )}
    </div>
  )
}

// ── Detail slide-over panel ────────────────────────────────────────────────────

function DetailPanel({ doc, onClose }) {
  const [expandedSection, setExpandedSection] = useState(null)

  if (!doc) return null

  const sections    = doc.sections    || []
  const feedbackLog = doc.feedback_log || []

  return (
    <motion.div
      key="detail-panel"
      initial={{ x: '100%' }}
      animate={{ x: 0 }}
      exit={{ x: '100%' }}
      transition={{ type: 'spring', damping: 28, stiffness: 220 }}
      style={{
        position: 'fixed', top: 0, right: 0, bottom: 0,
        width: 640, maxWidth: '90vw',
        background: 'var(--bg-surface)', borderLeft: '1px solid var(--border-soft)',
        zIndex: 300, display: 'flex', flexDirection: 'column',
        boxShadow: '-8px 0 40px rgba(0,0,0,0.4)',
      }}
    >
      {/* Header */}
      <div style={{
        padding: '16px 20px', borderBottom: '1px solid var(--border-subtle)',
        display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', gap: 12,
      }}>
        <div style={{ flex: 1, minWidth: 0 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 4 }}>
            <Archive size={15} color="var(--accent)" />
            <span style={{ fontSize: 11, color: 'var(--accent)', fontWeight: 500, textTransform: 'uppercase', letterSpacing: '0.06em' }}>
              Finalized Document
            </span>
          </div>
          <h2 style={{ fontFamily: 'var(--font-display)', fontSize: 17, color: 'var(--text-primary)', marginBottom: 2, wordBreak: 'break-word' }}>
            {doc.document_name || doc.document_type}
          </h2>
          <div style={{ fontSize: 12, color: 'var(--text-muted)' }}>
            {doc.metadata?.indication} · {doc.metadata?.phase}
          </div>
        </div>
        <div style={{ display: 'flex', gap: 8, alignItems: 'center', flexShrink: 0 }}>
          <ExportButton
            sessionId={doc.session_id}
            generationResult={doc}
            documentType={doc.document_name || doc.document_type}
          />
          <button onClick={onClose} style={{
            background: 'var(--bg-elevated)', border: '1px solid var(--border-soft)',
            borderRadius: 6, padding: '5px 7px', cursor: 'pointer', color: 'var(--text-muted)',
            display: 'flex',
          }}>
            <X size={14} />
          </button>
        </div>
      </div>

      {/* Scrollable body */}
      <div style={{ flex: 1, overflow: 'auto', padding: '16px 20px' }}>

        {/* Stats row */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 8, marginBottom: 20 }}>
          {[
            { label: 'Compliance', value: `${Math.round((doc.compliance_score || 0) * (doc.compliance_score > 1 ? 1 : 100))}%`, color: scoreColor(doc.compliance_score > 1 ? doc.compliance_score : doc.compliance_score * 100) },
            { label: 'Sections',   value: sections.length,    color: 'var(--info)' },
            { label: 'Words',      value: (doc.total_words || sections.reduce((s, x) => s + (x.word_count || 0), 0)).toLocaleString(), color: 'var(--text-primary)' },
            { label: 'Feedback',   value: feedbackLog.length, color: 'var(--accent)' },
          ].map(s => (
            <div key={s.label} style={{
              background: 'var(--bg-elevated)', borderRadius: 8, padding: '10px 12px', textAlign: 'center',
            }}>
              <div style={{ fontSize: 18, fontWeight: 600, color: s.color }}>{s.value}</div>
              <div style={{ fontSize: 10, color: 'var(--text-muted)' }}>{s.label}</div>
            </div>
          ))}
        </div>

        {/* Feedback log */}
        {feedbackLog.length > 0 && (
          <div style={{ marginBottom: 20 }}>
            <div style={{ fontSize: 12, fontWeight: 600, color: 'var(--text-secondary)', marginBottom: 8, display: 'flex', alignItems: 'center', gap: 6 }}>
              <MessageSquare size={13} /> Feedback Log ({feedbackLog.length})
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
              {feedbackLog.map((fb, i) => (
                <div key={i} style={{
                  background: 'var(--bg-elevated)', borderRadius: 8, padding: '10px 12px',
                  borderLeft: `3px solid ${fb.action === 'approve' ? 'var(--success)' : fb.action === 'revise' ? 'var(--warning)' : 'var(--danger)'}`,
                }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 4 }}>
                    <Badge
                      color={fb.action === 'approve' ? 'success' : fb.action === 'revise' ? 'warning' : 'danger'}
                      size="xs"
                    >
                      {fb.action}
                    </Badge>
                    <span style={{ fontSize: 11, color: 'var(--text-muted)' }}>
                      {fb.reviewer} · {fb.role}
                    </span>
                    <span style={{ fontSize: 10, color: 'var(--text-muted)', marginLeft: 'auto' }}>
                      {fb.section_id}
                    </span>
                  </div>
                  {fb.comment && (
                    <p style={{ fontSize: 12, color: 'var(--text-secondary)', margin: 0, lineHeight: 1.5 }}>
                      {fb.comment}
                    </p>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Sections accordion */}
        <div style={{ marginBottom: 8 }}>
          <div style={{ fontSize: 12, fontWeight: 600, color: 'var(--text-secondary)', marginBottom: 8, display: 'flex', alignItems: 'center', gap: 6 }}>
            <FileText size={13} /> Document Sections
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
            {sections.map((sec) => {
              const isOpen = expandedSection === sec.section_id
              const hasFeedback = feedbackLog.some(f => f.section_id === sec.section_id)
              return (
                <div key={sec.section_id} style={{
                  background: 'var(--bg-elevated)', borderRadius: 8,
                  border: '1px solid var(--border-subtle)', overflow: 'hidden',
                }}>
                  <button
                    onClick={() => setExpandedSection(isOpen ? null : sec.section_id)}
                    style={{
                      width: '100%', display: 'flex', alignItems: 'center', gap: 8,
                      padding: '9px 12px', background: 'none', border: 'none',
                      cursor: 'pointer', textAlign: 'left',
                    }}
                  >
                    {isOpen ? <ChevronDown size={12} color="var(--text-muted)" /> : <ChevronRight size={12} color="var(--text-muted)" />}
                    <span style={{ fontSize: 13, color: 'var(--text-primary)', flex: 1 }}>{sec.title}</span>
                    <span style={{ fontSize: 10, color: 'var(--text-muted)' }}>{sec.word_count}w</span>
                    {sec.revised && <Badge color="warning" size="xs">Edited</Badge>}
                    {hasFeedback && <Badge color="info" size="xs">Feedback</Badge>}
                    <Badge color="info" size="xs">{Math.round((sec.confidence_score || 0) * 100)}%</Badge>
                  </button>
                  <AnimatePresence>
                    {isOpen && (
                      <motion.div
                        initial={{ height: 0, opacity: 0 }}
                        animate={{ height: 'auto', opacity: 1 }}
                        exit={{ height: 0, opacity: 0 }}
                        transition={{ duration: 0.2 }}
                        style={{ overflow: 'hidden' }}
                      >
                        <div style={{
                          padding: '0 12px 12px', fontSize: 12, color: 'var(--text-secondary)',
                          lineHeight: 1.6, borderTop: '1px solid var(--border-subtle)',
                          whiteSpace: 'pre-wrap', maxHeight: 320, overflow: 'auto', paddingTop: 10,
                        }}>
                          {sec.content}
                        </div>
                      </motion.div>
                    )}
                  </AnimatePresence>
                </div>
              )
            })}
          </div>
        </div>
      </div>
    </motion.div>
  )
}

// ── Document card ──────────────────────────────────────────────────────────────

function DocCard({ doc, onView, onDelete }) {
  const score = doc.compliance_score > 1 ? doc.compliance_score : doc.compliance_score * 100
  return (
    <motion.div
      layout
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, scale: 0.97 }}
      transition={{ duration: 0.2 }}
    >
      <Card style={{ padding: '14px 16px', display: 'flex', flexDirection: 'column', gap: 10 }}>
        {/* Title row */}
        <div style={{ display: 'flex', alignItems: 'flex-start', gap: 10 }}>
          <div style={{
            width: 34, height: 34, borderRadius: 8, flexShrink: 0,
            background: 'var(--accent-glow)', border: '1px solid var(--accent-dim)',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
          }}>
            <FileText size={15} color="var(--accent)" />
          </div>
          <div style={{ flex: 1, minWidth: 0 }}>
            <div style={{ fontSize: 14, fontWeight: 600, color: 'var(--text-primary)', marginBottom: 2, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
              {doc.document_name || doc.document_type}
            </div>
            <div style={{ fontSize: 11, color: 'var(--text-muted)' }}>
              {doc.document_type} · {doc.indication} · {doc.phase}
            </div>
          </div>
          {/* Compliance badge */}
          <div style={{
            padding: '4px 10px', borderRadius: 20, fontSize: 11, fontWeight: 600,
            color: scoreColor(score), background: score >= 80 ? 'var(--success-dim)' : score >= 60 ? 'var(--warning-dim)' : 'rgba(240,68,68,0.1)',
            border: `1px solid ${scoreColor(score)}40`, whiteSpace: 'nowrap',
          }}>
            {Math.round(score)}% · {scoreLabel(score)}
          </div>
        </div>

        {/* Meta row */}
        <div style={{ display: 'flex', gap: 14, flexWrap: 'wrap' }}>
          <span style={{ fontSize: 11, color: 'var(--text-muted)', display: 'flex', alignItems: 'center', gap: 4 }}>
            <FileText size={10} /> {doc.section_count} sections
          </span>
          <span style={{ fontSize: 11, color: 'var(--text-muted)', display: 'flex', alignItems: 'center', gap: 4 }}>
            <Hash size={10} /> {(doc.total_words || 0).toLocaleString()} words
          </span>
          <span style={{ fontSize: 11, color: 'var(--text-muted)', display: 'flex', alignItems: 'center', gap: 4 }}>
            <MessageSquare size={10} /> {doc.feedback_count} feedback
          </span>
          <span style={{ fontSize: 11, color: 'var(--text-muted)', display: 'flex', alignItems: 'center', gap: 4 }}>
            <Calendar size={10} /> {fmtDate(doc.finalized_at)}
          </span>
        </div>

        {/* Session ID micro label */}
        <div style={{ fontSize: 10, color: 'var(--text-muted)', fontFamily: 'var(--font-mono)', opacity: 0.6 }}>
          {doc.session_id}
        </div>

        {/* Action row */}
        <div style={{ display: 'flex', gap: 8, alignItems: 'center', paddingTop: 4, borderTop: '1px solid var(--border-subtle)' }}>
          <button
            onClick={() => onView(doc.session_id)}
            style={{
              display: 'flex', alignItems: 'center', gap: 5,
              padding: '5px 12px', borderRadius: 6, border: '1px solid var(--border-soft)',
              background: 'var(--bg-elevated)', fontSize: 12, color: 'var(--text-secondary)',
              cursor: 'pointer', transition: 'all 0.15s',
            }}
            onMouseEnter={e => e.currentTarget.style.background = 'var(--bg-hover)'}
            onMouseLeave={e => e.currentTarget.style.background = 'var(--bg-elevated)'}
          >
            <Eye size={12} /> View Details
          </button>

          <ExportButton
            sessionId={doc.session_id}
            generationResult={doc}    /* full data loaded on demand */
            documentType={doc.document_name || doc.document_type}
          />

          <div style={{ flex: 1 }} />

          <button
            onClick={() => onDelete(doc.session_id)}
            style={{
              display: 'flex', alignItems: 'center', gap: 4,
              padding: '5px 10px', borderRadius: 6,
              border: '1px solid rgba(240,68,68,0.3)',
              background: 'rgba(240,68,68,0.06)', fontSize: 11,
              color: 'var(--danger)', cursor: 'pointer', transition: 'all 0.15s',
            }}
            onMouseEnter={e => { e.currentTarget.style.background = 'rgba(240,68,68,0.14)' }}
            onMouseLeave={e => { e.currentTarget.style.background = 'rgba(240,68,68,0.06)' }}
          >
            <Trash2 size={11} /> Delete
          </button>
        </div>
      </Card>
    </motion.div>
  )
}

// ── Main page ──────────────────────────────────────────────────────────────────

export default function FinalizedDocumentsPage() {
  const { serverStatus } = useAppStore()
  const [docs,          setDocs]          = useState([])
  const [loading,       setLoading]       = useState(false)
  const [detailId,      setDetailId]      = useState(null)
  const [detailDoc,     setDetailDoc]     = useState(null)
  const [loadingDetail, setLoadingDetail] = useState(false)

  const fetchList = useCallback(async () => {
    if (serverStatus !== 'online') return
    setLoading(true)
    try {
      const data = await apiService.listFinalizedDocuments()
      setDocs(data.documents || [])
    } catch (err) {
      toast.error(`Could not load finalized documents: ${err.message}`)
    } finally {
      setLoading(false)
    }
  }, [serverStatus])

  // Load on mount and whenever server comes online
  useEffect(() => { fetchList() }, [fetchList])

  const handleView = async (sessionId) => {
    setDetailId(sessionId)
    setLoadingDetail(true)
    try {
      const doc = await apiService.getFinalizedDocument(sessionId)
      setDetailDoc(doc)
    } catch (err) {
      toast.error(`Failed to load document: ${err.message}`)
      setDetailId(null)
    } finally {
      setLoadingDetail(false)
    }
  }

  const handleDelete = async (sessionId) => {
    if (!window.confirm('Permanently delete this finalized document?')) return
    try {
      await apiService.deleteFinalizedDocument(sessionId)
      setDocs(prev => prev.filter(d => d.session_id !== sessionId))
      if (detailId === sessionId) { setDetailId(null); setDetailDoc(null) }
      toast.success('Document deleted')
    } catch (err) {
      toast.error(`Delete failed: ${err.message}`)
    }
  }

  const closeDetail = () => { setDetailId(null); setDetailDoc(null) }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100vh', overflow: 'hidden' }}>
      <Topbar
        title="Finalized Documents"
        subtitle="Persistent archive · Survives server restarts"
      />

      <div style={{ flex: 1, overflow: 'auto', padding: '20px 24px' }}>

        {/* Page header */}
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 20 }}>
          <div>
            <h1 style={{ fontFamily: 'var(--font-display)', fontSize: 22, color: 'var(--text-primary)', marginBottom: 4 }}>
              Document Archive
            </h1>
            <p style={{ fontSize: 13, color: 'var(--text-muted)' }}>
              {docs.length} finalized document{docs.length !== 1 ? 's' : ''} stored on disk
            </p>
          </div>
          <button
            onClick={fetchList}
            disabled={loading || serverStatus !== 'online'}
            style={{
              display: 'flex', alignItems: 'center', gap: 6,
              padding: '7px 14px', borderRadius: 8, border: '1px solid var(--border-soft)',
              background: 'var(--bg-elevated)', fontSize: 12, color: 'var(--text-secondary)',
              cursor: loading ? 'wait' : 'pointer', opacity: serverStatus !== 'online' ? 0.5 : 1,
            }}
          >
            <RefreshCw size={12} style={{ animation: loading ? 'spin 1s linear infinite' : 'none' }} />
            Refresh
          </button>
        </div>

        {/* Offline notice */}
        {serverStatus !== 'online' && (
          <div style={{
            padding: '14px 18px', borderRadius: 10, marginBottom: 20,
            background: 'var(--warning-dim)', border: '1px solid rgba(245,166,35,0.3)',
            display: 'flex', alignItems: 'center', gap: 10, fontSize: 13, color: 'var(--warning)',
          }}>
            <AlertTriangle size={16} />
            Backend is offline — finalized documents are stored on the server and will appear once the API is online.
          </div>
        )}

        {/* Loading state */}
        {loading && (
          <div style={{ textAlign: 'center', padding: 40, color: 'var(--text-muted)' }}>
            <Loader size={24} style={{ animation: 'spin 1s linear infinite', marginBottom: 10 }} />
            <p style={{ fontSize: 13 }}>Loading archived documents…</p>
          </div>
        )}

        {/* Empty state */}
        {!loading && docs.length === 0 && serverStatus === 'online' && (
          <div style={{
            textAlign: 'center', padding: '60px 24px',
            background: 'var(--bg-elevated)', borderRadius: 12,
            border: '1px solid var(--border-subtle)',
          }}>
            <Archive size={36} color="var(--text-muted)" style={{ marginBottom: 12, opacity: 0.5 }} />
            <h3 style={{ fontSize: 16, color: 'var(--text-secondary)', marginBottom: 6 }}>No finalized documents yet</h3>
            <p style={{ fontSize: 13, color: 'var(--text-muted)', maxWidth: 380, margin: '0 auto' }}>
              Once you finalize a document on the Generate page, it will be saved here permanently — even after restarting the server.
            </p>
          </div>
        )}

        {/* Document grid */}
        {!loading && docs.length > 0 && (
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(480px, 1fr))', gap: 14 }}>
            <AnimatePresence>
              {docs.map(doc => (
                <DocCard
                  key={doc.session_id}
                  doc={doc}
                  onView={handleView}
                  onDelete={handleDelete}
                />
              ))}
            </AnimatePresence>
          </div>
        )}
      </div>

      {/* Detail panel overlay backdrop */}
      <AnimatePresence>
        {detailId && (
          <>
            <motion.div
              key="backdrop"
              initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
              style={{
                position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.45)', zIndex: 299,
              }}
              onClick={closeDetail}
            />
            {loadingDetail && (
              <div style={{
                position: 'fixed', top: '50%', right: 360, zIndex: 400,
                transform: 'translateY(-50%)', color: 'var(--text-muted)',
              }}>
                <Loader size={28} style={{ animation: 'spin 1s linear infinite' }} />
              </div>
            )}
            {detailDoc && (
              <DetailPanel doc={detailDoc} onClose={closeDetail} />
            )}
          </>
        )}
      </AnimatePresence>
    </div>
  )
}
