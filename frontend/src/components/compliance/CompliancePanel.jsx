import { ShieldCheck, ShieldX, AlertTriangle, Info, CheckCircle } from 'lucide-react'
import { Badge, Card } from '../ui/index.jsx'
import { SEVERITY_CONFIG, scoreColor } from '../../data/constants.js'

export default function CompliancePanel({ report }) {
  if (!report) return null
  const { overall_score, is_compliant, issues = [], guidelines_checked = [], entities_validated = {}, recommendations = [] } = report
  const score = Math.round(overall_score || 0)
  const sColor = scoreColor(score)
  const crits  = issues.filter(i => i.severity === 'critical')
  const warns  = issues.filter(i => i.severity === 'warning')
  const infos  = issues.filter(i => i.severity === 'info')

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
      {/* Score header */}
      <Card>
        <div style={{ display: 'flex', alignItems: 'center', gap: 20, flexWrap: 'wrap' }}>
          {/* Ring */}
          <div style={{ position: 'relative', width: 80, height: 80, flexShrink: 0 }}>
            <svg width="80" height="80" style={{ transform: 'rotate(-90deg)' }}>
              <circle cx="40" cy="40" r="34" fill="none" stroke="var(--border-subtle)" strokeWidth="6" />
              <circle cx="40" cy="40" r="34" fill="none" stroke={sColor} strokeWidth="6"
                strokeDasharray={`${2 * Math.PI * 34}`}
                strokeDashoffset={`${2 * Math.PI * 34 * (1 - score / 100)}`}
                strokeLinecap="round" style={{ transition: 'stroke-dashoffset 0.8s ease' }} />
            </svg>
            <div style={{ position: 'absolute', inset: 0, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center' }}>
              <span style={{ fontSize: 18, fontWeight: 700, color: sColor }}>{score}</span>
              <span style={{ fontSize: 9, color: 'var(--text-muted)', lineHeight: 1 }}>/100</span>
            </div>
          </div>

          {/* Summary */}
          <div style={{ flex: 1 }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 6 }}>
              {is_compliant
                ? <ShieldCheck size={16} color="var(--success)" />
                : <ShieldX    size={16} color="var(--danger)" />}
              <span style={{ fontSize: 14, fontWeight: 500, color: is_compliant ? 'var(--success)' : 'var(--danger)' }}>
                {is_compliant ? 'Compliant' : 'Non-Compliant'}
              </span>
            </div>
            <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap', marginBottom: 8 }}>
              {crits.length > 0 && <Badge color="danger"  size="xs">{crits.length} critical</Badge>}
              {warns.length > 0 && <Badge color="warning" size="xs">{warns.length} warnings</Badge>}
              {infos.length > 0 && <Badge color="info"    size="xs">{infos.length} info</Badge>}
              {issues.length === 0 && <Badge color="success" size="xs">All checks passed</Badge>}
            </div>
            <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap' }}>
              {guidelines_checked.map(g => (
                <span key={g} style={{ fontSize: 10, padding: '1px 6px', borderRadius: 4,
                  background: 'var(--bg-overlay)', color: 'var(--text-muted)', border: '1px solid var(--border-subtle)' }}>
                  {g}
                </span>
              ))}
            </div>
          </div>
        </div>
      </Card>

      {/* Issues */}
      {issues.length > 0 && (
        <Card>
          <div style={{ fontSize: 12, fontWeight: 500, color: 'var(--text-secondary)', marginBottom: 10,
            textTransform: 'uppercase', letterSpacing: '0.05em' }}>Issues Found</div>
          {issues.map((issue, i) => {
            const cfg  = SEVERITY_CONFIG[issue.severity] || SEVERITY_CONFIG.info
            const Icon = { critical: ShieldX, warning: AlertTriangle, info: Info }[issue.severity] || Info
            return (
              <div key={i} style={{ padding: '10px 12px', borderRadius: 'var(--radius-md)', marginBottom: 6,
                background: cfg.bg, border: `1px solid ${cfg.border}` }}>
                <div style={{ display: 'flex', alignItems: 'flex-start', gap: 8 }}>
                  <Icon size={13} color={cfg.color} style={{ marginTop: 1, flexShrink: 0 }} />
                  <div style={{ flex: 1 }}>
                    <div style={{ fontSize: 12, color: 'var(--text-primary)', marginBottom: 2 }}>{issue.description}</div>
                    <div style={{ fontSize: 11, color: 'var(--text-muted)' }}>→ {issue.suggestion}</div>
                    {issue.regulatory_ref && (
                      <div style={{ fontSize: 10, color: cfg.color, marginTop: 3 }}>Ref: {issue.regulatory_ref}</div>
                    )}
                  </div>
                  <Badge color={issue.severity === 'critical' ? 'danger' : issue.severity === 'warning' ? 'warning' : 'info'} size="xs">
                    {issue.rule_id || cfg.label}
                  </Badge>
                </div>
              </div>
            )
          })}
        </Card>
      )}

      {/* Validated entities */}
      {Object.keys(entities_validated).length > 0 && (
        <Card>
          <div style={{ fontSize: 12, fontWeight: 500, color: 'var(--text-secondary)', marginBottom: 10,
            textTransform: 'uppercase', letterSpacing: '0.05em' }}>Validated Entities</div>
          {Object.entries(entities_validated).map(([type, items]) => (
            <div key={type} style={{ marginBottom: 8 }}>
              <div style={{ fontSize: 11, color: 'var(--text-muted)', marginBottom: 4 }}>{type}</div>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: 4 }}>
                {items.slice(0, 6).map(item => (
                  <span key={item} style={{ fontSize: 11, padding: '2px 7px', borderRadius: 10,
                    background: 'var(--bg-overlay)', color: 'var(--text-secondary)',
                    border: '1px solid var(--border-subtle)' }}>
                    {item}
                  </span>
                ))}
              </div>
            </div>
          ))}
        </Card>
      )}

      {/* Recommendations */}
      {recommendations.length > 0 && (
        <Card>
          <div style={{ fontSize: 12, fontWeight: 500, color: 'var(--text-secondary)', marginBottom: 10,
            textTransform: 'uppercase', letterSpacing: '0.05em' }}>Recommendations</div>
          {recommendations.map((rec, i) => (
            <div key={i} style={{ display: 'flex', gap: 8, marginBottom: 7, alignItems: 'flex-start' }}>
              <CheckCircle size={12} color="var(--accent)" style={{ marginTop: 2, flexShrink: 0 }} />
              <span style={{ fontSize: 12, color: 'var(--text-secondary)', lineHeight: 1.5 }}>{rec}</span>
            </div>
          ))}
        </Card>
      )}
    </div>
  )
}
