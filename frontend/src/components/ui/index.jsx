import { forwardRef } from 'react'
import { Loader2 } from 'lucide-react'

// ─── Button ──────────────────────────────────────────────────────────────────
// In your Button component, replace the variant style logic with:

const variantStyles = {
  primary: {
    background: 'var(--accent)',
    color: '#fff',
    border: 'none',
    boxShadow: '0 1px 3px rgba(0,0,0,0.2)',
  },
  ghost: {
    background: 'transparent',
    color: 'var(--text-secondary)',
    border: '1px solid var(--border-soft)',
  },
  success: {
    background: 'var(--success)',
    color: '#fff',
    border: 'none',
  },
  danger: {
    background: 'var(--danger)',
    color: '#fff',
    border: 'none',
  },
  default: {
    background: 'var(--bg-elevated)',
    color: 'var(--text-secondary)',
    border: '1px solid var(--border-soft)',
  },
}

const sizeStyles = {
  xs: 'px-2.5 py-1 text-xs gap-1',
  sm: 'px-3 py-1.5 text-sm gap-1.5',
  md: 'px-4 py-2 text-sm gap-2',
  lg: 'px-6 py-2.5 text-base gap-2',
}

export function Button({
  variant = 'primary', size = 'md', loading, disabled,
  className = '', children, icon, iconRight, ...props
}) {
  const base = [
    'inline-flex items-center justify-center font-medium rounded-lg border',
    'transition-all duration-150 select-none cursor-pointer',
    'disabled:opacity-40 disabled:cursor-not-allowed',
    variantStyles[variant] || variantStyles.primary,
    sizeStyles[size] || sizeStyles.md,
    'rounded-lg', 
    'tracking-wide',
    className,
  ].join(' ')

  return (
    <button className={base} disabled={disabled || loading} {...props}
      style={{
        backgroundColor: variant === 'primary' ? 'var(--accent)' : undefined,
        color: variant === 'primary' ? 'var(--bg-base)' : undefined,
        borderColor: variant === 'primary' ? 'var(--accent)' : 'var(--border-soft)',
        ...props.style,
      }}>
      {loading
        ? <Loader2 size={14} style={{ animation: 'spin 1s linear infinite' }} />
        : icon}
      {children}
      {!loading && iconRight}
    </button>
  )
}

// ─── Badge ───────────────────────────────────────────────────────────────────
const badgeColors = {
  default: { bg: 'var(--bg-overlay)', color: 'var(--text-secondary)', border: 'var(--border-soft)' },
  accent:  { bg: 'var(--accent-glow)', color: 'var(--accent-text)', border: 'var(--accent-dim)' },
  success: { bg: 'var(--success-dim)', color: 'var(--success)', border: 'rgba(52,201,123,0.3)' },
  warning: { bg: 'var(--warning-dim)', color: 'var(--warning)', border: 'rgba(245,166,35,0.3)' },
  danger:  { bg: 'var(--danger-dim)', color: 'var(--danger)', border: 'rgba(240,68,68,0.3)' },
  info:    { bg: 'var(--info-dim)', color: 'var(--info)', border: 'rgba(74,158,255,0.3)' },
}

export function Badge({ color = 'default', size = 'sm', children, icon }) {
  const c = badgeColors[color] || badgeColors.default
  const pad = size === 'xs' ? '2px 6px' : size === 'sm' ? '3px 8px' : '4px 10px'
  const fs = size === 'xs' ? '10px' : size === 'sm' ? '11px' : '12px'
  return (
    <span style={{
      display: 'inline-flex', alignItems: 'center', gap: 4,
      background: c.bg, color: c.color, border: `1px solid ${c.border}`,
      padding: pad, borderRadius: 20, fontSize: fs, fontWeight: 500, whiteSpace: 'nowrap',
    }}>
      {icon && <span style={{ display: 'flex', alignItems: 'center' }}>{icon}</span>}
      {children}
    </span>
  )
}

// ─── Card ────────────────────────────────────────────────────────────────────
export function Card({ children, className = '', padding = true, hover = false, ...props }) {
  return (
    <div
      className={className}
      style={{
        background: 'var(--bg-surface)',
        border: '1px solid var(--border-subtle)',
        borderRadius: 'var(--radius-lg)',
        padding: padding ? '1.25rem' : 0,
        transition: hover ? 'border-color 0.2s, background 0.2s' : undefined,
        ...props.style,
      }}
      {...props}
    >
      {children}
    </div>
  )
}

// ─── Input ───────────────────────────────────────────────────────────────────
export const Input = forwardRef(function Input({
  label, error, hint, icon, className = '', containerClass = '', ...props
}, ref) {
  return (
    <div className={containerClass} style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
      {label && (
        <label style={{ fontSize: 12, fontWeight: 500, color: 'var(--text-secondary)', letterSpacing: '0.02em' }}>
          {label}
        </label>
      )}
      <div style={{ position: 'relative' }}>
        {icon && (
          <span style={{
            position: 'absolute', left: 10, top: '50%', transform: 'translateY(-50%)',
            color: 'var(--text-muted)', display: 'flex', pointerEvents: 'none',
          }}>
            {icon}
          </span>
        )}
        <input
          ref={ref}
          className={className}
          style={{
            width: '100%',
            background: 'var(--bg-elevated)',
            border: `1px solid ${error ? 'var(--danger)' : 'var(--border-soft)'}`,
            borderRadius: 'var(--radius-md)',
            padding: icon ? '8px 10px 8px 32px' : '8px 10px',
            fontSize: 13,
            color: 'var(--text-primary)',
            outline: 'none',
            transition: 'border-color 0.15s',
            fontFamily: 'var(--font-body)',
          }}
          onFocus={e => e.target.style.borderColor = 'var(--accent)'}
          onBlur={e => e.target.style.borderColor = error ? 'var(--danger)' : 'var(--border-soft)'}
          {...props}
        />
      </div>
      {error && <span style={{ fontSize: 11, color: 'var(--danger)' }}>{error}</span>}
      {hint && !error && <span style={{ fontSize: 11, color: 'var(--text-muted)' }}>{hint}</span>}
    </div>
  )
})

// ─── Select ──────────────────────────────────────────────────────────────────
export const Select = forwardRef(function Select({
  label, error, hint, children, containerClass = '', ...props
}, ref) {
  return (
    <div className={containerClass} style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
      {label && (
        <label style={{ fontSize: 12, fontWeight: 500, color: 'var(--text-secondary)', letterSpacing: '0.02em' }}>
          {label}
        </label>
      )}
      <select
        ref={ref}
        style={{
          width: '100%',
          background: 'var(--bg-elevated)',
          border: `1px solid ${error ? 'var(--danger)' : 'var(--border-soft)'}`,
          borderRadius: 'var(--radius-md)',
          padding: '8px 10px',
          fontSize: 13,
          color: 'var(--text-primary)',
          outline: 'none',
          cursor: 'pointer',
          fontFamily: 'var(--font-body)',
          transition: 'border-color 0.15s',
          appearance: 'none',
          backgroundImage: `url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 24 24' fill='none' stroke='%2350596a' stroke-width='2'%3E%3Cpolyline points='6 9 12 15 18 9'/%3E%3C/svg%3E")`,
          backgroundRepeat: 'no-repeat',
          backgroundPosition: 'right 10px center',
          paddingRight: 28,
        }}
        onFocus={e => e.target.style.borderColor = 'var(--accent)'}
        onBlur={e => e.target.style.borderColor = error ? 'var(--danger)' : 'var(--border-soft)'}
        {...props}
      >
        {children}
      </select>
      {error && <span style={{ fontSize: 11, color: 'var(--danger)' }}>{error}</span>}
      {hint && !error && <span style={{ fontSize: 11, color: 'var(--text-muted)' }}>{hint}</span>}
    </div>
  )
})

// ─── Textarea ────────────────────────────────────────────────────────────────
export const Textarea = forwardRef(function Textarea({
  label, error, hint, rows = 4, containerClass = '', ...props
}, ref) {
  return (
    <div className={containerClass} style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
      {label && (
        <label style={{ fontSize: 12, fontWeight: 500, color: 'var(--text-secondary)', letterSpacing: '0.02em' }}>
          {label}
        </label>
      )}
      <textarea
        ref={ref}
        rows={rows}
        style={{
          width: '100%',
          background: 'var(--bg-elevated)',
          border: `1px solid ${error ? 'var(--danger)' : 'var(--border-soft)'}`,
          borderRadius: 'var(--radius-md)',
          padding: '8px 10px',
          fontSize: 13,
          color: 'var(--text-primary)',
          outline: 'none',
          resize: 'vertical',
          fontFamily: 'var(--font-body)',
          lineHeight: 1.6,
          transition: 'border-color 0.15s',
        }}
        onFocus={e => e.target.style.borderColor = 'var(--accent)'}
        onBlur={e => e.target.style.borderColor = error ? 'var(--danger)' : 'var(--border-soft)'}
        {...props}
      />
      {error && <span style={{ fontSize: 11, color: 'var(--danger)' }}>{error}</span>}
      {hint && !error && <span style={{ fontSize: 11, color: 'var(--text-muted)' }}>{hint}</span>}
    </div>
  )
})

// ─── Divider ─────────────────────────────────────────────────────────────────
export function Divider({ label }) {
  if (!label) return <hr style={{ border: 'none', borderTop: '1px solid var(--border-subtle)', margin: '1rem 0' }} />
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: 12, margin: '1rem 0' }}>
      <div style={{ flex: 1, height: 1, background: 'var(--border-subtle)' }} />
      <span style={{ fontSize: 11, color: 'var(--text-muted)', fontWeight: 500, letterSpacing: '0.05em', textTransform: 'uppercase' }}>{label}</span>
      <div style={{ flex: 1, height: 1, background: 'var(--border-subtle)' }} />
    </div>
  )
}

// ─── Spinner ─────────────────────────────────────────────────────────────────
export function Spinner({ size = 20, color = 'var(--accent)' }) {
  return (
    <div style={{
      width: size, height: size,
      border: `2px solid var(--border-soft)`,
      borderTopColor: color,
      borderRadius: '50%',
      animation: 'spin 0.8s linear infinite',
      flexShrink: 0,
    }} />
  )
}

// ─── Tooltip ─────────────────────────────────────────────────────────────────
export function Tooltip({ children, tip }) {
  return (
    <span style={{ position: 'relative', display: 'inline-flex' }}
      onMouseEnter={e => {
        const el = e.currentTarget.querySelector('.tip')
        if (el) el.style.opacity = '1'
      }}
      onMouseLeave={e => {
        const el = e.currentTarget.querySelector('.tip')
        if (el) el.style.opacity = '0'
      }}>
      {children}
      <span className="tip" style={{
        position: 'absolute', bottom: '110%', left: '50%', transform: 'translateX(-50%)',
        background: 'var(--bg-overlay)', color: 'var(--text-primary)',
        fontSize: 11, padding: '4px 8px', borderRadius: 6,
        border: '1px solid var(--border-soft)', whiteSpace: 'nowrap',
        opacity: 0, transition: 'opacity 0.15s', pointerEvents: 'none', zIndex: 100,
      }}>
        {tip}
      </span>
    </span>
  )
}

// ─── Progress bar ─────────────────────────────────────────────────────────────
export function ProgressBar({ value = 0, max = 100, color = 'var(--accent)', height = 4 }) {
  const pct = Math.min(100, Math.max(0, (value / max) * 100))
  return (
    <div style={{ height, background: 'var(--bg-overlay)', borderRadius: height, overflow: 'hidden' }}>
      <div style={{
        height: '100%', width: `${pct}%`, background: color,
        borderRadius: height, transition: 'width 0.4s ease',
      }} />
    </div>
  )
}

// ─── Stats card ──────────────────────────────────────────────────────────────
export function StatCard({ label, value, icon, color = 'var(--accent)' }) {
  return (
    <div style={{
      background: 'var(--bg-elevated)', border: '1px solid var(--border-subtle)',
      borderRadius: 'var(--radius-md)', padding: '12px 16px', textAlign: 'center',
    }}>
      {icon && <div style={{ color, marginBottom: 4, display: 'flex', justifyContent: 'center' }}>{icon}</div>}
      <div style={{ fontSize: 22, fontWeight: 600, color, lineHeight: 1.2 }}>{value}</div>
      <div style={{ fontSize: 11, color: 'var(--text-muted)', marginTop: 3 }}>{label}</div>
    </div>
  )
}
