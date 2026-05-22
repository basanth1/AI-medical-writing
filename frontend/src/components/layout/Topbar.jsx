import { useAppStore } from '../../store/appStore.js'
import { Badge } from '../ui/index.jsx'
import ThemeToggle from '../ui/ThemeToggle.jsx'
import { HelpCircle } from 'lucide-react'

const STEP_LABELS = ['Configure', 'Generating', 'Review', 'Done']

export default function Topbar({ title, subtitle }) {
  const {
    currentStep, sessionId, userPrefs,
    ollamaAvailable, ollamaModel,
    groqAvailable, activeGenerator,
  } = useAppStore()

  // Derive a concise status pill
  const llmBadge = (() => {
    if (activeGenerator === 'ollama')
      return { label: `gpt-oss:120b`, color: 'success' }
    if (activeGenerator === 'groq')
      return { label: `llama-3.3-70b ↩ fallback`, color: 'warning' }
    return { label: 'template (no LLM)', color: 'danger' }
  })()

  return (
    <header style={{
      height: 56, flexShrink: 0, position: 'sticky', top: 0, zIndex: 5,
      background: 'var(--bg-surface)',
      borderBottom: '1px solid var(--border-subtle)',
      display: 'flex', alignItems: 'center', justifyContent: 'space-between',
      padding: '0 24px', transition: 'background 0.25s',
    }}>
      <div>
        <h1 style={{ fontSize: 15, fontWeight: 500, color: 'var(--text-primary)' }}>{title}</h1>
        {subtitle && <p style={{ fontSize: 11, color: 'var(--text-muted)' }}>{subtitle}</p>}
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
        {/* LLM status pill */}
        <Badge color={llmBadge.color} size="sm">
          ⚡ {llmBadge.label}
        </Badge>

        {sessionId && (
          <Badge color="accent" size="sm">Session {sessionId.slice(-8)}</Badge>
        )}

        {/* Pipeline breadcrumb */}
        {currentStep > 0 && (
          <div style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
            {STEP_LABELS.map((label, i) => (
              <div key={i} style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
                <div title={label} style={{
                  width: 20, height: 20, borderRadius: '50%',
                  fontSize: 10, fontWeight: 600,
                  display: 'flex', alignItems: 'center', justifyContent: 'center',
                  background: i < currentStep  ? 'var(--success-dim)'
                               : i === currentStep ? 'var(--accent-glow)' : 'var(--bg-overlay)',
                  color: i < currentStep  ? 'var(--success)'
                          : i === currentStep ? 'var(--accent)' : 'var(--text-muted)',
                  border: `1px solid ${i < currentStep  ? 'var(--success)'
                            : i === currentStep ? 'var(--accent-dim)' : 'var(--border-subtle)'}`,
                  transition: 'all 0.3s',
                }}>
                  {i < currentStep ? '✓' : i + 1}
                </div>
                {i < STEP_LABELS.length - 1 && (
                  <div style={{
                    width: 14, height: 1,
                    background: i < currentStep ? 'var(--success)' : 'var(--border-subtle)',
                  }} />
                )}
              </div>
            ))}
          </div>
        )}

        <ThemeToggle />

        <button style={{
          background: 'none', border: 'none', cursor: 'pointer',
          color: 'var(--text-muted)', display: 'flex', padding: 4, borderRadius: 6,
        }}>
          <HelpCircle size={16} />
        </button>

        {/* User avatar */}
        <div style={{
          width: 28, height: 28, borderRadius: '50%',
          background: 'var(--accent-glow)', border: '1px solid var(--accent-dim)',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          fontSize: 11, fontWeight: 600, color: 'var(--accent-text)', cursor: 'pointer',
        }}
        onClick={() => window.location.href = '/settings'}>
          {userPrefs.name ? userPrefs.name[0].toUpperCase() : 'U'}
        </div>
      </div>
    </header>
  )
}
