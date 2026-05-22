// frontend/src/components/document/ExportButton.jsx
//
// Selective export dropdown — md / json / docx
// Uses the server-side /export/{session_id}?format= endpoint when a session
// exists (so all feedback rewrites are included), falls back to client-side
// Markdown when offline.

import { useState, useRef, useEffect } from 'react'
import { Download, FileText, FileJson, FileType, ChevronDown, Loader } from 'lucide-react'
import { apiService } from '../../services/api.js'
import { useAppStore } from '../../store/appStore.js'
import toast from 'react-hot-toast'

const FORMATS = [
  {
    id: 'md',
    label: 'Markdown',
    ext: '.md',
    mime: 'text/markdown',
    icon: FileText,
    description: 'Human-readable, tables preserved',
  },
  {
    id: 'json',
    label: 'JSON',
    ext: '.json',
    mime: 'application/json',
    icon: FileJson,
    description: 'Structured data with confidence scores',
  },
  {
    id: 'docx',
    label: 'Word',
    ext: '.docx',
    mime: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    icon: FileType,
    description: 'Microsoft Word, cover page included',
  },
]

/**
 * Props:
 *   sessionId        — backend session id (null = offline/client fallback)
 *   generationResult — full result object for client-side fallback
 *   documentType     — string label for filename
 *   disabled         — grey out entirely
 *   size             — 'sm' | 'md' (default 'sm')
 */
export default function ExportButton({
  sessionId,
  generationResult,
  documentType = 'Document',
  disabled = false,
  size = 'sm',
}) {
  const { serverStatus } = useAppStore()
  const [open, setOpen]         = useState(false)
  const [loading, setLoading]   = useState(null)   // format id currently loading
  const ref = useRef(null)

  // Close on outside click
  useEffect(() => {
    if (!open) return
    const handle = (e) => { if (ref.current && !ref.current.contains(e.target)) setOpen(false) }
    document.addEventListener('mousedown', handle)
    return () => document.removeEventListener('mousedown', handle)
  }, [open])

  const safeName = (documentType || 'Document').replace(/\s+/g, '_')

  const downloadBlob = (blob, filename) => {
    const url = URL.createObjectURL(blob)
    const a   = document.createElement('a')
    a.href     = url
    a.download = filename
    a.click()
    URL.revokeObjectURL(url)
  }

  const clientFallback = (fmt) => {
    const sections = generationResult?.sections || []
    if (fmt.id === 'md') {
      const md = `# ${documentType}\n\n---\n\n` +
        sections.map(s => `## ${s.title}\n\n${s.content}`).join('\n\n---\n\n')
      downloadBlob(new Blob([md], { type: fmt.mime }), `${safeName}${fmt.ext}`)
    } else if (fmt.id === 'json') {
      downloadBlob(
        new Blob([JSON.stringify(generationResult, null, 2)], { type: fmt.mime }),
        `${safeName}${fmt.ext}`
      )
    } else {
      toast('DOCX export requires the backend to be online.', { icon: 'ℹ️' })
      return
    }
    toast.success(`Downloaded as ${fmt.label}`)
  }

  const handleSelect = async (fmt) => {
    setOpen(false)
    if (!generationResult) return toast.error('No document to export')

    // Server-side path — includes all rewrites + placeholder fills
    if (sessionId && serverStatus === 'online') {
      setLoading(fmt.id)
      try {
        const resp = await apiService.exportDocument(sessionId, fmt.id)
          if (!(resp instanceof Blob)) {
    console.error('Expected Blob, but got:', typeof resp);

  }
  
        downloadBlob(resp, `${safeName}${fmt.ext}`)
        toast.success(`Downloaded as ${fmt.label}`)
      } catch (err) {
        toast.error(`Export failed: ${err.message}`)
        // Graceful client fallback for md/json
        if (fmt.id !== 'docx') clientFallback(fmt)
      } finally {
        setLoading(null)
      }
      return
    }

    // Offline / no session — client-side fallback
    clientFallback(fmt)
  }

  const isLoading = loading !== null

  const btnStyle = {
    display: 'inline-flex', alignItems: 'center', gap: size === 'sm' ? 5 : 7,
    padding: size === 'sm' ? '6px 12px' : '8px 16px',
    background: 'var(--bg-elevated)', border: '1px solid var(--border-soft)',
    borderRadius: 'var(--radius-md)', cursor: disabled || isLoading ? 'not-allowed' : 'pointer',
    fontSize: size === 'sm' ? 12 : 13, color: 'var(--text-secondary)',
    opacity: disabled ? 0.45 : 1, transition: 'all 0.15s', position: 'relative',
    whiteSpace: 'nowrap',
  }

  return (
    <div ref={ref} style={{ position: 'relative', display: 'inline-block' }}>
      {/* Trigger button */}
      <button
        style={{
                padding: '6px 14px', fontSize: '0.85rem', borderRadius: '0.5rem',
                display: 'inline-flex', alignItems: 'center', gap: '0.25rem',
                backgroundColor: 'transparent', color: 'var(--white)',
                border: '1px solid rgba(19, 18, 18, 0.4)', cursor: 'pointer',
                              }}
        disabled={disabled || isLoading}
        onClick={() => !disabled && !isLoading && setOpen(p => !p)}
        onMouseEnter={e => { if (!disabled && !isLoading) e.currentTarget.style.background = 'var(--bg-overlay)' }}
        onMouseLeave={e => { e.currentTarget.style.background = 'var(--bg-elevated)' }}
      >
        {isLoading
          ? <Loader size={13} style={{ animation: 'spin 1s linear infinite' }} />
          : <Download size={13} />
        }
        Export
        <ChevronDown
          size={13}
          style={{ opacity: 0.4, transform: open ? 'rotate(180deg)' : 'rotate(0deg)', transition: 'transform 0.15s' }}
        />
      </button>

      {/* Dropdown */}
      {open && (
        <div style={{
          position: 'absolute', top: 'calc(100% + 6px)', right: 0, zIndex: 200,
          background: 'var(--bg-elevated)', border: '1px solid var(--border-soft)',
          borderRadius: 'var(--radius-md)', boxShadow: '0 8px 24px rgba(0,0,0,0.35)',
          minWidth: 210, overflow: 'hidden',
        }}>
          {/* Header */}
          <div style={{
            padding: '8px 12px 6px', fontSize: 10, fontWeight: 600,
            color: 'var(--text-muted)', letterSpacing: '0.08em', textTransform: 'uppercase',
            borderBottom: '1px solid var(--border-subtle)',
          }}>
            Download as
          </div>

          {FORMATS.map(fmt => {
            const Icon = fmt.icon
            const isThisLoading = loading === fmt.id
            return (
              <button
                key={fmt.id}
                onClick={() => handleSelect(fmt)}
                disabled={isThisLoading}
                style={{
                  width: '100%', display: 'flex', alignItems: 'center', gap: 10,
                  padding: '9px 12px', background: 'none', border: 'none',
                  cursor: 'pointer', textAlign: 'left', transition: 'background 0.12s',
                  opacity: isThisLoading ? 0.6 : 1,
                }}
                onMouseEnter={e => { e.currentTarget.style.background = 'var(--bg-hover)' }}
                onMouseLeave={e => { e.currentTarget.style.background = 'none' }}
              >
                <div style={{
                  width: 28, height: 28, borderRadius: 6,
                  background: 'var(--bg-overlay)', border: '1px solid var(--border-subtle)',
                  display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0,
                }}>
                  {isThisLoading
                    ? <Loader size={13} color="var(--accent)" style={{ animation: 'spin 1s linear infinite' }} />
                    : <Icon size={13} color="var(--accent)" />
                  }
                </div>
                <div>
                  <div style={{ fontSize: 13, color: 'var(--text-primary)', fontWeight: 500, lineHeight: 1.3 }}>
                    {fmt.label}
                    <span style={{ fontSize: 10, color: 'var(--text-muted)', fontWeight: 400, marginLeft: 5 }}>
                      {fmt.ext}
                    </span>
                  </div>
                  <div style={{ fontSize: 10, color: 'var(--text-muted)', lineHeight: 1.3 }}>
                    {fmt.description}
                  </div>
                </div>
              </button>
            )
          })}

          {/* Offline notice */}
          {serverStatus !== 'online' && (
            <div style={{
              padding: '6px 12px 8px', fontSize: 10, color: 'var(--warning)',
              borderTop: '1px solid var(--border-subtle)', display: 'flex', alignItems: 'center', gap: 5,
            }}>
              ⚠ Offline — DOCX requires the backend
            </div>
          )}
        </div>
      )}
    </div>
  )
}
