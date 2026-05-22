import { useState, useEffect } from 'react'
import { useForm } from 'react-hook-form'
import { CheckCircle, XCircle, Edit3, MessageSquare, Send, ThumbsUp, ThumbsDown, Star } from 'lucide-react'
import { Button, Card, Input, Select, Textarea, Badge } from '../ui/index.jsx'
import { useAppStore } from '../../store/appStore.js'
import { apiService } from '../../services/api.js'
import { FEEDBACK_ACTIONS, FEEDBACK_SEVERITY_OPTIONS, REVIEWER_ROLES, QUALITY_DIMENSIONS } from '../../data/constants.js'
import toast from 'react-hot-toast'

const ACTION_ICONS = { approve: ThumbsUp, revise: Edit3, reject: ThumbsDown }

function FeedbackCard({ fb }) {
  const cfg = FEEDBACK_ACTIONS[fb.action] || FEEDBACK_ACTIONS.approve
  const Icon = ACTION_ICONS[fb.action] || ThumbsUp
  return (
    <div style={{ padding: '12px 14px', borderRadius: 'var(--radius-md)', marginBottom: 8,
      background: cfg.bg, border: `1px solid ${cfg.border}` }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 6 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <Icon size={13} color={cfg.color} />
          <span style={{ fontSize: 13, fontWeight: 500, color: 'var(--text-primary)' }}>{fb.reviewer_name || 'Anonymous'}</span>
          <span style={{ fontSize: 11, color: 'var(--text-muted)' }}>{fb.reviewer_role}</span>
        </div>
        <div style={{ display: 'flex', gap: 6, alignItems: 'center' }}>
          <Badge color={fb.action === 'approve' ? 'success' : fb.action === 'reject' ? 'danger' : 'warning'} size="xs">
            {cfg.label}
          </Badge>
          <span style={{ fontSize: 10, color: 'var(--text-muted)' }}>
            {new Date(fb.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
          </span>
        </div>
      </div>
      {fb.section_id && (
        <div style={{ fontSize: 11, color: 'var(--text-muted)', marginBottom: 4 }}>
          Section: <code style={{ background: 'var(--bg-overlay)', padding: '1px 4px', borderRadius: 3 }}>{fb.section_id}</code>
        </div>
      )}
      {fb.comment && <p style={{ fontSize: 12, color: 'var(--text-secondary)', lineHeight: 1.5 }}>{fb.comment}</p>}
      {fb.severity && fb.severity !== 'minor' && (
        <div style={{ marginTop: 4 }}>
          <Badge color={fb.severity === 'critical' ? 'danger' : 'warning'} size="xs">{fb.severity}</Badge>
        </div>
      )}
    </div>
  )
}

export default function FeedbackMechanism({ sessionId , onSectionUpdated}) {
  const { sections,setSections,addFeedback, feedbackLog, userPrefs, setGenerationResult,setComplianceReport } = useAppStore()
  const [submitting, setSubmitting] = useState(false)
  const [showRevisionBox, setShowRevisionBox] = useState(false)
  const [activeTab, setActiveTab] = useState('submit')
  const { register, handleSubmit, reset, watch, setValue, formState: { errors } } = useForm({
    defaultValues: {
      section_id:'',
      reviewer_name: userPrefs.name || '',
      reviewer_role: userPrefs.role || 'Medical Writer',
      comment: '', action: 'approve',
      severity: 'minor', revised_text: '', rating: 0,
    }
  })
  useEffect(() => {
  if (sections.length > 0) {
    setValue('section_id', sections[0].section_id)
  }
}, [sections])

  const action = watch('action')
  const rating = watch('rating')

  const onSubmit = async (data) => {
    setSubmitting(true)
    try {
      const payload = {
        section_id: data.section_id || null,
        reviewer_name: data.reviewer_name, reviewer_role: data.reviewer_role,
        comment: data.comment, action: data.action, severity: data.severity,
        revised_text: showRevisionBox && data.revised_text ? data.revised_text : null,
      }
      const response = sessionId
  ? await apiService.submitFeedback(sessionId, payload)
  : null
console.log("Feedback API response:", response)
if (response?.sections) {
  setSections(response.sections)
}
if (response?.compliance_report) {
  
  toast.success('Compliance report updated based on feedback')
  setGenerationResult(prev => prev ?({ ...prev, 
    sections: response.sections || prev.sections,
    compliance_report: response.compliance_report }): prev)
    setComplianceReport(response.compliance_report)
}

// Show per-section compliance result in toast if available
if (response?.updated_section) {
  const sec = response.updated_section
  const compliant = sec.section_compliant
  const issues    = sec.compliance_flags || []
  const conf      = Math.round((sec.confidence_score || 0) * 100)

  if (compliant) {
    toast.success(`Section rewritten ✓  Confidence: ${conf}%  Compliant`, { icon: '✅' })
  } else {
    toast(`Section rewritten · ${conf}% confidence · ${issues.length} compliance issue(s)`,
      { icon: '⚠️', duration: 5000 })
  }
}

// Update document-level analytics in store if you have an analytics slice
// if (response?.doc_analytics) {
//   setDocAnalytics(response.doc_analytics)
// }

if (onSectionUpdated) onSectionUpdated(data.section_id || payload.section_id)
    console.log("Updating sections:", response)

      addFeedback({ ...payload, rating: data.rating, timestamp: new Date().toISOString() })
      toast.success(`Feedback submitted: ${FEEDBACK_ACTIONS[data.action]?.label}`)
      if (data.action === 'reject') {
        toast.success("Section removed from document")
      }
      if (data.action === 'revise') {
        toast.success("Section rewritten using AI")
      }
      if (data.action === 'approve') {
        toast.success("Section approved")
      }
      reset({ ...data, comment: '', revised_text: '' })
      setShowRevisionBox(false)
    } catch (err) {
      toast.error(err.message || 'Failed to submit feedback')
    } finally {
      setSubmitting(false)
    }
  }

  const Tab = ({ id, label, count }) => (
    <button onClick={() => setActiveTab(id)} style={{
      padding: '7px 14px', border: 'none',
      borderBottom: `2px solid ${activeTab === id ? 'var(--accent)' : 'transparent'}`,
      background: 'transparent', fontSize: 13,
      fontWeight: activeTab === id ? 500 : 400,
      color: activeTab === id ? 'var(--accent-text)' : 'var(--text-muted)',
      cursor: 'pointer', display: 'flex', alignItems: 'center', gap: 5,
    }}>
      {label}
      {count > 0 && (
        <span style={{ fontSize: 10, background: 'var(--accent-glow)', color: 'var(--accent)', borderRadius: 10, padding: '1px 5px' }}>
          {count}
        </span>
      )}
    </button>
  )

  return (
    <div>
      <div style={{ display: 'flex', borderBottom: '1px solid var(--border-subtle)', marginBottom: 16 }}>
        <Tab id="submit" label="Submit Review" count={0} />
        <Tab id="log"    label="Review Log"   count={feedbackLog.length} />
        <Tab id="rating" label="Rating"       count={0} />
      </div>

      {activeTab === 'submit' && (
        <form onSubmit={handleSubmit(onSubmit)}>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 10, marginBottom: 10 }}>
            <Input label="Reviewer Name *" {...register('reviewer_name', { required: 'Required' })}
              error={errors.reviewer_name?.message} placeholder="Dr. Jane Smith" />
            <Select label="Role" {...register('reviewer_role')}>
              {REVIEWER_ROLES.map(r => <option key={r}>{r}</option>)}
            </Select>
          </div>
          <Select label="Section (optional)" {...register('section_id')}  >
            <option value="">— Entire document —</option>
            {sections.map(s => <option key={s.section_id} value={s.section_id}>{s.title}</option>)}
          </Select>

          {/* Action buttons */}
          <div style={{ marginBottom: 10 }}>
            <div style={{ fontSize: 12, fontWeight: 500, color: 'var(--text-secondary)', marginBottom: 8 }}>Review Decision *</div>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3,1fr)', gap: 8 }}>
              {Object.entries(FEEDBACK_ACTIONS).map(([key, cfg]) => {
                const Icon = ACTION_ICONS[key]
                const isSelected = action === key
                return (
                  <button key={key} type="button"
                    onClick={() => { setValue('action', key); if (key === 'revise') setShowRevisionBox(true) }}
                    style={{
                      padding: '10px 8px',
                      border: `1.5px solid ${isSelected ? cfg.color : 'var(--border-subtle)'}`,
                      borderRadius: 'var(--radius-md)',
                      background: isSelected ? cfg.bg : 'var(--bg-elevated)',
                      cursor: 'pointer', display: 'flex', flexDirection: 'column',
                      alignItems: 'center', gap: 4, transition: 'all 0.15s',
                    }}>
                    <Icon size={16} color={isSelected ? cfg.color : 'var(--text-muted)'} />
                    <span style={{ fontSize: 11, fontWeight: isSelected ? 500 : 400,
                      color: isSelected ? cfg.color : 'var(--text-muted)' }}>{cfg.label}</span>
                  </button>
                )
              })}
            </div>
          </div>

          <Textarea label="Comment *" {...register('comment', { required: 'Please add a comment' })}
            error={errors.comment?.message} rows={3}
            placeholder="Describe your review observations, requested changes, or approval rationale…" />

          <Select label="Issue Severity" {...register('severity')} >
            {FEEDBACK_SEVERITY_OPTIONS.map(s => <option key={s}>{s}</option>)}
          </Select>

          {showRevisionBox && (
            <div style={{ marginBottom: 10 }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 4 }}>
                <span style={{ fontSize: 12, fontWeight: 500, color: 'var(--text-secondary)' }}>Revised Text (optional)</span>
                <button type="button" onClick={() => setShowRevisionBox(false)}
                  style={{ fontSize: 10, color: 'var(--text-muted)', background: 'none', border: 'none', cursor: 'pointer' }}>
                  Remove ×
                </button>
              </div>
              <Textarea {...register('revised_text')} rows={5}
                placeholder="Paste revised section content here…" />
            </div>
          )}

          {action === 'revise' && !showRevisionBox && (
            <button type="button" onClick={() => setShowRevisionBox(true)}
              style={{ fontSize: 11, color: 'var(--accent)', background: 'none', border: 'none',
                cursor: 'pointer', display: 'flex', alignItems: 'center', gap: 4, marginBottom: 10 }}>
              <Edit3 size={11} /> Add revised text
            </button>
          )}

          <div style={{
  display: 'flex',             // Enable flexbox layout
  justifyContent: 'center',    // Center horizontally
  alignItems: 'center',        // Center vertically
                     // Space between child elements
}}>
  <Button 
    type="submit" 
    loading={submitting} 
    icon={<Send size={14} />} 
    style={{
      padding: '10px 20px',          // Adjust padding for better spacing
      fontSize: '14px',              // Font size for readability
      borderRadius: '8px',           // Rounded corners
      fontWeight: '500',             // Slightly bolder text for prominence
      backgroundColor: '#4CAF50',   // Green background for positive action
      color: 'white',                // White text for contrast
      border: 'none',                // Remove border
      cursor: 'pointer',            // Pointer cursor on hover
      transition: 'background-color 0.3s ease, transform 0.3s ease', // Smooth transition effects
    }}
  >
    Submit Review
  </Button>
</div>
        </form>
      )}

      {activeTab === 'log' && (
        <div>
          {feedbackLog.length === 0 ? (
            <div style={{ textAlign: 'center', padding: '2rem', color: 'var(--text-muted)' }}>
              <MessageSquare size={32} style={{ marginBottom: 8, opacity: 0.4 }} />
              <p style={{ fontSize: 13 }}>No feedback submitted yet.</p>
            </div>
          ) : (
            <>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3,1fr)', gap: 8, marginBottom: 12 }}>
                {Object.entries(FEEDBACK_ACTIONS).map(([key, cfg]) => (
                  <div key={key} style={{ background: cfg.bg, border: `1px solid ${cfg.border}`,
                    borderRadius: 'var(--radius-md)', padding: '8px 12px', textAlign: 'center' }}>
                    <div style={{ fontSize: 20, fontWeight: 700, color: cfg.color }}>
                      {feedbackLog.filter(f => f.action === key).length}
                    </div>
                    <div style={{ fontSize: 10, color: 'var(--text-muted)' }}>{cfg.label}</div>
                  </div>
                ))}
              </div>
              {[...feedbackLog].reverse().map((fb, i) => <FeedbackCard key={i} fb={fb} />)}
            </>
          )}
        </div>
      )}

      {activeTab === 'rating' && (
        <Card style={{ textAlign: 'center', padding: 24 }}>
          <div style={{ fontFamily: 'var(--font-display)', fontSize: 18, marginBottom: 8 }}>Rate This Document</div>
          <p style={{ fontSize: 13, color: 'var(--text-muted)', marginBottom: 20 }}>
            How well does this AI-generated document meet regulatory standards?
          </p>
          <div style={{ display: 'flex', justifyContent: 'center', gap: 12, marginBottom: 20 }}>
            {[1,2,3,4,5].map(n => (
              <button key={n} type="button" onClick={() => setValue('rating', n)}
                style={{ background: 'none', border: 'none', cursor: 'pointer', padding: 4 }}>
                <Star size={28} fill={n <= rating ? 'var(--accent)' : 'none'}
                  color={n <= rating ? 'var(--accent)' : 'var(--border-mid)'} />
              </button>
            ))}
          </div>
          <p style={{ fontSize: 12, color: 'var(--text-muted)' }}>
            {rating === 0 ? 'Select a rating'
              : rating <= 2 ? 'Needs significant improvement'
              : rating === 3 ? 'Meets basic requirements'
              : rating === 4 ? 'Good quality, minor issues'
              : 'Excellent regulatory quality'}
          </p>
          <div style={{ marginTop: 20 }}>
            {QUALITY_DIMENSIONS.map(dim => (
              <div key={dim} style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 10 }}>
                <span style={{ fontSize: 12, color: 'var(--text-secondary)', width: 140, flexShrink: 0 }}>{dim}</span>
                <div style={{ flex: 1, display: 'flex', gap: 4 }}>
                  {[1,2,3,4,5].map(n => (
                    <div key={n} style={{ flex: 1, height: 5, borderRadius: 3,
                      background: n <= rating ? 'var(--accent)' : 'var(--bg-overlay)',
                      transition: 'background 0.2s' }} />
                  ))}
                </div>
              </div>
            ))}
          </div>
        </Card>
      )}
    </div>
  )
}
