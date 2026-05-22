import { useState } from 'react'
import { motion } from 'framer-motion'
import { MessageSquare, Filter, Download, Trash2, CheckCircle, XCircle, Edit3 } from 'lucide-react'
import Topbar from '../components/layout/Topbar.jsx'
import FeedbackMechanism from '../components/feedback/FeedbackMechanism.jsx'
import { Button, Card, Badge, StatCard } from '../components/ui/index.jsx'
import { useAppStore } from '../store/appStore'
import toast from 'react-hot-toast'

export default function FeedbackPage() {
  const { generationResult, sessionId, feedbackLog, clearFeedback } = useAppStore()
  const [filter, setFilter] = useState('all')

  const sections = generationResult?.sections || []
  const filtered = filter === 'all' ? feedbackLog : feedbackLog.filter(f => f.action === filter)

  const approved = feedbackLog.filter(f => f.action === 'approve').length
  const revisions = feedbackLog.filter(f => f.action === 'revise').length
  const rejected  = feedbackLog.filter(f => f.action === 'reject').length

  const exportLog = () => {
    const data = JSON.stringify(feedbackLog, null, 2)
    const blob = new Blob([data], { type: 'application/json' })
    const a = document.createElement('a')
    a.href = URL.createObjectURL(blob)
    a.download = `feedback_log_${sessionId || 'session'}.json`
    a.click()
    toast.success('Feedback log exported')
  }

  const FILTER_BTNS = [
    { id: 'all',     label: 'All',      count: feedbackLog.length },
    { id: 'approve', label: 'Approved', count: approved },
    { id: 'revise',  label: 'Revisions',count: revisions },
    { id: 'reject',  label: 'Rejected', count: rejected },
  ]

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100vh', overflow: 'hidden' }}>
      <Topbar title="Feedback & Review" subtitle="Human-in-the-loop medical writer review system" />
      <div style={{ flex: 1, overflow: 'auto', padding: '20px 24px' }}>

        {/* Stats */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4,1fr)', gap: 10, marginBottom: 20 }}>
          <StatCard label="Total Reviews" value={feedbackLog.length} icon={<MessageSquare size={14} />} color="var(--info)" />
          <StatCard label="Approved" value={approved} icon={<CheckCircle size={14} />} color="var(--success)" />
          <StatCard label="Needs Revision" value={revisions} icon={<Edit3 size={14} />} color="var(--warning)" />
          <StatCard label="Rejected" value={rejected} icon={<XCircle size={14} />} color="var(--danger)" />
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: '1fr 360px', gap: 16 }}>
          {/* Left — log & filters */}
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 14 }}>
              <div style={{ display: 'flex', gap: 6 }}>
                {FILTER_BTNS.map(btn => (
                  <button key={btn.id} onClick={() => setFilter(btn.id)} style={{
                    padding: '5px 12px', borderRadius: 20, fontSize: 12, fontWeight: 500,
                    border: `1px solid ${filter === btn.id ? 'var(--accent-dim)' : 'var(--border-subtle)'}`,
                    background: filter === btn.id ? 'var(--accent-glow)' : 'var(--bg-elevated)',
                    color: filter === btn.id ? 'var(--accent-text)' : 'var(--text-secondary)',
                    cursor: 'pointer',
                  }}>
                    {btn.label} {btn.count > 0 && <span style={{ marginLeft: 4, opacity: 0.7 }}>({btn.count})</span>}
                  </button>
                ))}
              </div>
              <div style={{ flex: 1 }} />
              {feedbackLog.length > 0 && (
                <>
                  <Button variant="ghost" size="xs" icon={<Download size={12} />} onClick={exportLog}>Export</Button>
                  <Button variant="ghost" size="xs" icon={<Trash2 size={12} />} onClick={() => { clearFeedback(); toast.success('Feedback cleared') }}>Clear</Button>
                </>
              )}
            </div>

            {filtered.length === 0 ? (
              <div style={{ textAlign: 'center', padding: '3rem', color: 'var(--text-muted)' }}>
                <MessageSquare size={40} style={{ marginBottom: 12, opacity: 0.3 }} />
                <p style={{ fontSize: 13 }}>{feedbackLog.length === 0 ? 'No feedback submitted yet.' : 'No feedback matches this filter.'}</p>
              </div>
            ) : (
              <div>
                {[...filtered].reverse().map((fb, i) => {
                  const colors = { approve: { bg: 'var(--success-dim)', border: 'rgba(52,201,123,0.25)', color: 'var(--success)' }, revise: { bg: 'var(--warning-dim)', border: 'rgba(245,166,35,0.25)', color: 'var(--warning)' }, reject: { bg: 'var(--danger-dim)', border: 'rgba(240,68,68,0.25)', color: 'var(--danger)' } }
                  const c = colors[fb.action] || colors.approve
                  return (
                    <motion.div key={i} initial={{ opacity: 0, x: -8 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: i * 0.03 }}>
                      <div style={{ padding: '12px 14px', borderRadius: 'var(--radius-md)', background: c.bg, border: `1px solid ${c.border}`, marginBottom: 8 }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 5 }}>
                          <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
                            <span style={{ fontSize: 13, fontWeight: 500, color: 'var(--text-primary)' }}>{fb.reviewer_name || 'Anonymous'}</span>
                            <span style={{ fontSize: 11, color: 'var(--text-muted)' }}>{fb.reviewer_role}</span>
                          </div>
                          <div style={{ display: 'flex', gap: 6 }}>
                            <Badge color={fb.action === 'approve' ? 'success' : fb.action === 'reject' ? 'danger' : 'warning'} size="xs">
                              {fb.action}
                            </Badge>
                            {fb.severity && fb.severity !== 'minor' && <Badge color="warning" size="xs">{fb.severity}</Badge>}
                            <span style={{ fontSize: 10, color: 'var(--text-muted)' }}>
                              {new Date(fb.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                            </span>
                          </div>
                        </div>
                        {fb.section_id && <div style={{ fontSize: 11, color: c.color, marginBottom: 4 }}>§ {fb.section_id}</div>}
                        {fb.comment && <p style={{ fontSize: 12, color: 'var(--text-secondary)', lineHeight: 1.5 }}>{fb.comment}</p>}
                        {fb.revised_text && (
                          <details style={{ marginTop: 6 }}>
                            <summary style={{ fontSize: 11, color: 'var(--text-muted)', cursor: 'pointer' }}>View revised text</summary>
                            <div style={{ marginTop: 6, padding: 8, background: 'var(--bg-overlay)', borderRadius: 6, fontSize: 11, color: 'var(--text-secondary)', fontFamily: 'var(--font-mono)', whiteSpace: 'pre-wrap', maxHeight: 150, overflowY: 'auto' }}>
                              {fb.revised_text}
                            </div>
                          </details>
                        )}
                      </div>
                    </motion.div>
                  )
                })}
              </div>
            )}
          </div>

          {/* Right — submit new feedback */}
          <div>
            <Card>
              <h3 style={{ fontSize: 13, fontWeight: 500, marginBottom: 14, display: 'flex', alignItems: 'center', gap: 6 }}>
                <MessageSquare size={14} color="var(--accent)" /> Submit Review
              </h3>
              <FeedbackMechanism sections={sections} sessionId={sessionId} />
            </Card>
          </div>
        </div>
      </div>
    </div>
  )
}
