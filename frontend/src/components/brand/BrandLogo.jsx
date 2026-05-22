export function BrandMark({ size = 68, image = '/new circulants logo.png', alt = 'Circulants AI' }) {
  return (
    <div style={{
      width: size,
      height: size,
      borderRadius: 'var(--radius-md)',
      background: '#ffffff',
      border: '1px solid rgba(13, 27, 46, 0.14)',
      boxShadow: '0 8px 22px rgba(0, 0, 0, 0.14)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      overflow: 'hidden',
      flexShrink: 0,
    }}>
      <img
        src={image}
        alt={alt}
        style={{ width: 34, height: 34, objectFit: 'cover', display: 'block' }}
      />
    </div>
  )
}

export default function BrandLogo({ markSize = 34, compact = false, title = 'TrialDoc', subtitle = 'AI Generator' }) {
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: 10, minWidth: 0 }}>
      <BrandMark size={markSize} />
      {!compact && (
        <div style={{ minWidth: 0, overflow: 'hidden' }}>
          <div style={{
            fontFamily: 'var(--font-display)',
            fontSize: 14,
            fontWeight: 700,
            color: 'var(--text-primary)',
            whiteSpace: 'nowrap',
          }}>
            {title}
          </div>
          <div style={{
            fontSize: 9,
            color: 'var(--text-muted)',
            letterSpacing: '0.08em',
            textTransform: 'uppercase',
            whiteSpace: 'nowrap',
          }}>
            {subtitle}
          </div>
        </div>
      )}
    </div>
  )
}
