import { useAppStore } from '../store/appStore'
import Topbar from '../components/layout/Topbar.jsx'
import { Card, StatCard, Badge } from '../components/ui/index.jsx'
import { BarChart3, FileText, MessageSquare, ShieldCheck, Zap, TrendingUp } from 'lucide-react'

function MiniBar({ value, max, color = 'var(--accent)' }) {
  return (
    <div style={{ height: 6, background: 'var(--bg-overlay)', borderRadius: 3, overflow: 'hidden', flex: 1 }}>
      <div style={{ height: '100%', width: `${Math.min(100, (value / max) * 100)}%`, background: color, borderRadius: 3, transition: 'width 0.6s ease' }} />
    </div>
  )
}

function ScoreGauge({ score, label }) {
  const color = score >= 85 ? 'var(--success)' : score >= 70 ? 'var(--warning)' : 'var(--danger)'
  return (
    <div style={{ textAlign: 'center' }}>
      <div style={{ position: 'relative', width: 70, height: 70, margin: '0 auto 8px' }}>
        <svg width="70" height="70" style={{ transform: 'rotate(-90deg)' }}>
          <circle cx="35" cy="35" r="28" fill="none" stroke="var(--border-subtle)" strokeWidth="5" />
          <circle cx="35" cy="35" r="28" fill="none" stroke={color} strokeWidth="5"
            strokeDasharray={`${2 * Math.PI * 28}`}
            strokeDashoffset={`${2 * Math.PI * 28 * (1 - score / 100)}`}
            strokeLinecap="round" style={{ transition: 'stroke-dashoffset 0.8s ease' }} />
        </svg>
        <div style={{ position: 'absolute', inset: 0, display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 15, fontWeight: 700, color }}>
          {score}
        </div>
      </div>
      <div style={{ fontSize: 11, color: 'var(--text-muted)' }}>{label}</div>
    </div>
  )
}

export default function AnalyticsPage() {
  const { generationResult, feedbackLog, documentType, sections: storeSections, complianceReport } = useAppStore()

  // const sections = generationResult?.sections || []
  const sections = storeSections.length > 0 ? storeSections : (generationResult?.sections || [])
  const liveReport = complianceReport ?? generationResult?.compliance_report
  const totalWords = sections.reduce((s, sec) => s + (sec.word_count || 0), 0)
  const avgConf = sections.length ? Math.round(sections.reduce((s, sec) => s + (sec.confidence_score || 0), 0) / sections.length * 100) : 0
  const complianceScore = Math.round(liveReport?.overall_score || 0)
  const issues = liveReport?.issues || []
  const crits = issues.filter(i => i.severity === 'critical').length
  const warns = issues.filter(i => i.severity === 'warning').length

  const feedbackByAction = {
    approve: feedbackLog.filter(f => f.action === 'approve').length,
    revise: feedbackLog.filter(f => f.action === 'revise').length,
    reject: feedbackLog.filter(f => f.action === 'reject').length,
  }
  const maxFb = Math.max(...Object.values(feedbackByAction), 1)

  const sectionWordData = sections.map(s => ({ title: s.title.slice(0, 28), words: s.word_count, conf: Math.round((s.confidence_score || 0) * 100) }))
  const maxWords = Math.max(...sectionWordData.map(s => s.words), 1)

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100vh', overflow: 'hidden' }}>
      <Topbar title="Analytics" subtitle="Document generation metrics and quality indicators" />
      <div style={{ flex: 1, overflow: 'auto', padding: '20px 24px' }}>

        {!generationResult ? (
          <div style={{ textAlign: 'center', padding: '4rem', color: 'var(--text-muted)' }}>
            <BarChart3 size={48} style={{ marginBottom: 16, opacity: 0.3 }} />
            <p style={{ fontSize: 14 }}>Generate a document first to see analytics.</p>
          </div>
        ) : (
          <div style={{ maxWidth: 1000, margin: '0 auto' }}>
            {/* KPIs */}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4,1fr)', gap: 10, marginBottom: 16 }}>
              <StatCard label="Total Words" value={totalWords.toLocaleString()} icon={<FileText size={14} />} color="var(--accent)" />
              <StatCard label="Avg Confidence" value={`${avgConf}%`} icon={<Zap size={14} />} color="var(--info)" />
              <StatCard label="Compliance" value={`${complianceScore}%`} icon={<ShieldCheck size={14} />} color={complianceScore >= 70 ? 'var(--success)' : 'var(--danger)'} />
              <StatCard label="Feedback Items" value={feedbackLog.length} icon={<MessageSquare size={14} />} color="var(--warning)" />
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: 14 }}>
              {/* Section word counts */}
              <Card>
                <h3 style={{ fontSize: 13, fontWeight: 500, marginBottom: 14 }}>Section Word Counts & Confidence</h3>
                {sectionWordData.length === 0 ? (
                  <p style={{ fontSize: 12, color: 'var(--text-muted)' }}>No sections generated.</p>
                ) : sectionWordData.map((s, i) => (
                  <div key={i} style={{ marginBottom: 10 }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 3 }}>
                      <span style={{ fontSize: 11, color: 'var(--text-secondary)', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap', maxWidth: '55%' }}>{s.title}</span>
                      <div style={{ display: 'flex', gap: 8, fontSize: 10, color: 'var(--text-muted)', flexShrink: 0 }}>
                        <span>{s.words}w</span>
                        <span style={{ color: s.conf >= 80 ? 'var(--success)' : s.conf >= 70 ? 'var(--warning)' : 'var(--danger)' }}>{s.conf}%</span>
                      </div>
                    </div>
                    <div style={{ display: 'flex', gap: 6, alignItems: 'center' }}>
                      <MiniBar value={s.words} max={maxWords} color="var(--accent)" />
                      <MiniBar value={s.conf} max={100} color={s.conf >= 80 ? 'var(--success)' : s.conf >= 70 ? 'var(--warning)' : 'var(--danger)'} />
                    </div>
                  </div>
                ))}
              </Card>

              {/* Right column */}
              <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
                {/* Quality gauges */}
                <Card>
                  <h3 style={{ fontSize: 13, fontWeight: 500, marginBottom: 14 }}>Quality Scores</h3>
                  <div style={{ display: 'flex', justifyContent: 'space-around' }}>
                    <ScoreGauge score={complianceScore} label="Compliance" />
                    <ScoreGauge score={avgConf} label="Confidence" />
                  </div>
                </Card>

                {/* Compliance issues breakdown */}
                <Card>
                  <h3 style={{ fontSize: 13, fontWeight: 500, marginBottom: 12 }}>Issues Breakdown</h3>
                  {[['Critical', crits, 'var(--danger)'], ['Warnings', warns, 'var(--warning)'], ['Info', issues.length - crits - warns, 'var(--info)']].map(([label, count, color]) => (
                    <div key={label} style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 8 }}>
                      <span style={{ fontSize: 11, color: 'var(--text-muted)', width: 60 }}>{label}</span>
                      <div style={{ flex: 1, height: 6, background: 'var(--bg-overlay)', borderRadius: 3, overflow: 'hidden' }}>
                        <div style={{ height: '100%', width: `${issues.length ? (count / issues.length) * 100 : 0}%`, background: color, borderRadius: 3 }} />
                      </div>
                      <span style={{ fontSize: 11, fontWeight: 600, color, width: 16, textAlign: 'right' }}>{count}</span>
                    </div>
                  ))}
                </Card>

                {/* Feedback breakdown */}
                <Card>
                  <h3 style={{ fontSize: 13, fontWeight: 500, marginBottom: 12 }}>Review Actions</h3>
                  {[['Approved', feedbackByAction.approve, 'var(--success)'], ['Revisions', feedbackByAction.revise, 'var(--warning)'], ['Rejected', feedbackByAction.reject, 'var(--danger)']].map(([label, count, color]) => (
                    <div key={label} style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 8 }}>
                      <span style={{ fontSize: 11, color: 'var(--text-muted)', width: 60 }}>{label}</span>
                      <MiniBar value={count} max={maxFb} color={color} />
                      <span style={{ fontSize: 11, fontWeight: 600, color, width: 16, textAlign: 'right' }}>{count}</span>
                    </div>
                  ))}
                </Card>

                {/* Document info */}
                <Card>
                  <h3 style={{ fontSize: 13, fontWeight: 500, marginBottom: 10 }}>Document Info</h3>
                  {[['Type', documentType], ['Sections', sections.length], ['Sources', generationResult.retrieved_sources?.length || 0], ['Model', generationResult.model_used || 'Groq']].map(([k, v]) => (
                    <div key={k} style={{ display: 'flex', justifyContent: 'space-between', fontSize: 12, marginBottom: 6 }}>
                      <span style={{ color: 'var(--text-muted)' }}>{k}</span>
                      <span style={{ fontWeight: 500, color: 'var(--text-secondary)', textAlign: 'right', maxWidth: '55%', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{v}</span>
                    </div>
                  ))}
                </Card>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
