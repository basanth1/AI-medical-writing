import { useState, useEffect, useCallback } from 'react'
import { Tag, CheckCircle, AlertTriangle, ChevronRight, Loader } from 'lucide-react'
import { Button, Card, Input, Badge } from '../ui/index.jsx'
import { apiService } from '../../services/api.js'
import toast from 'react-hot-toast'

const PLACEHOLDER_RE = /\[([A-Za-z][A-Za-z0-9_\-/ ]{1,80})\]/g

function normalizePlaceholderToken(token) {
  return token.trim().toUpperCase().replace(/[^A-Z0-9]+/g, '_').replace(/^_+|_+$/g, '').replace(/_+/g, '_')
}

function findPlaceholderTarget(sections, replacements) {
  const filledTokens = new Set(Object.keys(replacements).map(normalizePlaceholderToken))

  for (const section of sections || []) {
    const lines = String(section.content || '').split('\n')
    for (let lineIndex = 0; lineIndex < lines.length; lineIndex += 1) {
      PLACEHOLDER_RE.lastIndex = 0
      let match
      while ((match = PLACEHOLDER_RE.exec(lines[lineIndex])) !== null) {
        const token = normalizePlaceholderToken(match[1])
        if (filledTokens.has(token)) {
          return {
            sectionId: section.section_id,
            line: lineIndex + 1,
            token,
            value: replacements[token],
            lineText: lines[lineIndex].trim(),
          }
        }
      }
    }
  }

  return null
}

/**
 * PlaceholderManager
 * 
 * Fetches all remaining [PLACEHOLDER] tokens from the session,
 * lets the user fill them in, and sends a single batch request
 * to replace them in all sections.
 * 
 * Props:
 *   sessionId       – current session
 *   onFilled(remaining) – called after a successful fill so parent can refresh
 */
export default function PlaceholderManager({ sessionId, sections = [], onFilled }) {
  const [placeholders, setPlaceholders] = useState([])  // [{token, label, example}]
  const [values,       setValues]       = useState({})   // {token: userValue}
  const [loading,      setLoading]      = useState(false)
  const [saving,       setSaving]       = useState(false)
  const [lastFilled,   setLastFilled]   = useState(null) // {filled, remaining}

  // Fetch placeholders from backend
  const fetchPlaceholders = useCallback(async () => {
    if (!sessionId) return
    setLoading(true)
    try {
      const data = await apiService.getPlaceholders(sessionId)
      setPlaceholders(data.placeholders || [])
      // Pre-fill values dict with empty strings
      setValues(prev => {
        const init = {}
        for (const p of data.placeholders || []) init[p.token] = prev[p.token] || ''
        return init
      })
    } catch (err) {
      toast.error(`Could not load placeholders: ${err.message}`)
    } finally {
      setLoading(false)
    }
  }, [sessionId])

  useEffect(() => { fetchPlaceholders() }, [fetchPlaceholders])

  const handleChange = (token, val) => {
    setValues(prev => ({ ...prev, [token]: val }))
  }

// const refreshDocument = async () => {
//   try {
//     // Re-fetch updated session data from the backend
//     const updatedSession = await apiService.getSession(sessionId);

//     // Assuming you want to update the generation result waith the latest session data
//     setGenerationResult(prev => ({
//       ...prev,
//       sections: updatedSession.sections,
//     }));

//     // Optionally, reset the document or handle additional UI changes
//     // This will trigger a re-render in the `DocumentViewer` with the updated sections
//     toast.success('Document refreshed with updated placeholders.');
//   } catch (err) {
//     toast.error('Failed to refresh document.');
//   }
// };

  const handleFill = async () => {
    const replacements = {}
    for (const [k, v] of Object.entries(values)) {
      if (v && v.trim()) replacements[k] = v.trim()
    }
    if (!Object.keys(replacements).length) {
      toast.error('Enter at least one value before filling.')
      return
    }
    const fillTarget = findPlaceholderTarget(sections, replacements)
    setSaving(true)
    const t = toast.loading('Filling placeholders…')
    try {
      const result = await apiService.fillPlaceholders(sessionId, replacements)
      setLastFilled({
        filled:    result.placeholders_filled,
        remaining: result.remaining,
      })
      // Refresh placeholder list
      setPlaceholders(
        result.remaining.map(token => ({
          token,
          label:   token.replace(/_/g, ' '),
          example: '',
        }))
      )
      // Clear filled values
      const newVals = {}
      for (const t of result.remaining) newVals[t] = ''
      setValues(newVals)

      // if (result.placeholders_filled > 0) {
      //   toast.success(
      //     `${result.placeholders_filled} placeholder(s) filled. ` +
      //     `${result.remaining.length} remaining.`,
      //     { id: t }
      //   )
      //   if (result?.sections_updated){ 
      //     console.log('Calling onFilled with sections:', result.sections_updated);
      //     onFilled(result.sections_updated);
      //     // await refreshDocument();
      //    }
      // } 
          if (result.placeholders_filled > 0) {
      toast.success(
        `${result.placeholders_filled} placeholder(s) filled. ${result.remaining.length} remaining.`,
        { id: t }
      )

      if (onFilled) onFilled(result.remaining, fillTarget)
    }
      else {
        toast('No placeholders were filled — check your values.', { id: t, icon: '⚠️' })
      }
    } catch (err) {
      toast.error(err.message, { id: t })
    } finally {
      setSaving(false)
    }
  }

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: '24px', color: 'var(--text-muted)' }}>
        <Loader size={20} style={{ animation: 'spin 1s linear infinite', marginBottom: 8 }} />
        <p style={{ fontSize: 12 }}>Scanning for placeholders…</p>
      </div>
    )
  }

  if (!placeholders.length) {
    return (
      <div style={{ padding: '16px 0', textAlign: 'center', color: 'var(--text-muted)' }}>
        <CheckCircle size={24} color="var(--success)" style={{ marginBottom: 8 }} />
        <p style={{ fontSize: 13, color: 'var(--success)' }}>
          No placeholders remaining — document is ready to export.
        </p>
        {lastFilled && (
          <p style={{ fontSize: 11, color: 'var(--text-muted)', marginTop: 4 }}>
            {lastFilled.filled} placeholder(s) filled in last batch.
          </p>
        )}
      </div>
    )
  }

  const filledCount = Object.values(values).filter(v => v && v.trim()).length

  return (
    <div>
      <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 14 }}>
        <AlertTriangle size={15} color="var(--warning)" />
        <span style={{ fontSize: 13, fontWeight: 500, color: 'var(--text-primary)' }}>
          {placeholders.length} placeholder{placeholders.length !== 1 ? 's' : ''} require your input
        </span>
        <Badge color="warning" size="xs">{placeholders.length}</Badge>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: 10, marginBottom: 14 }}>
        {placeholders.map(p => (
          <div key={p.token} style={{ display: 'flex', alignItems: 'flex-start', gap: 10 }}>
            {/* Token badge */}
            <div style={{
              padding: '4px 8px', borderRadius: 'var(--radius-sm)',
              background: 'var(--warning-dim)', border: '1px solid rgba(245,166,35,0.3)',
              fontSize: 10, fontFamily: 'var(--font-mono)', color: 'var(--warning)',
              whiteSpace: 'nowrap', marginTop: 24, flexShrink: 0,
            }}>
              [{p.token}]
            </div>
            {/* Input */}
            <div style={{ flex: 1 }}>
              <Input
                label={p.label || p.token.replace(/_/g, ' ')}
                value={values[p.token] || ''}
                onChange={e => handleChange(p.token, e.target.value)}
                placeholder={p.example || `Enter ${(p.label || p.token).toLowerCase()}…`}
              />
            </div>
            {/* Status dot */}
            <div style={{ marginTop: 26, flexShrink: 0 }}>
              {values[p.token]?.trim()
                ? <CheckCircle size={16} color="var(--success)" />
                : <div style={{ width: 16, height: 16, borderRadius: '50%', border: '2px solid var(--border-mid)' }} />
              }
            </div>
          </div>
        ))}
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
        <span style={{ fontSize: 12, color: 'var(--text-muted)' }}>
          {filledCount} / {placeholders.length} filled
        </span>
        <div style={{ flex: 1 }} />
        <Button onClick={fetchPlaceholders} style={{
                padding: '6px 14px', fontSize: '0.7rem', borderRadius: '0.5rem',
                display: 'inline-flex', alignItems: 'center', gap: '0.25rem',
                backgroundColor: 'transparent', color: 'var(--grey)',
                border: '1px solid rgba(255,255,255,0.4)', cursor: 'pointer',
              }}          >
          Refresh
        </Button>
        <Button
          onClick={handleFill}
          loading={saving}
          disabled={filledCount === 0}
          icon={<ChevronRight size={14} />}
          style={{
                padding: '6px 14px', fontSize: '0.7rem', borderRadius: '0.5rem',
                display: 'inline-flex', alignItems: 'center', gap: '0.25rem',
                backgroundColor: 'transparent', color: 'var(--success)',
                border: '1px solid rgba(255,255,255,0.4)', cursor: 'pointer',
              }}>
          Apply {filledCount > 0 ? `(${filledCount})` : ''}
        </Button>
      </div>
    </div>
  )
}
