import { useState, useEffect } from 'react'
import { ChevronRight, ChevronDown, Copy, Edit3, Check, BookOpen, FileText } from 'lucide-react'
import { Badge, Button, Card, StatCard } from '../ui/index.jsx'
import { useAppStore } from '../../store/appStore'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'

function highlightFilledText(children, text) {
  if (!text) return children
  const target = String(text)

  const visit = (child, key = 'highlight') => {
    if (typeof child === 'string') {
      const idx = child.indexOf(target)
      if (idx === -1) return child

      return (
        <>
          {child.slice(0, idx)}
          <mark
            className="placeholder-fill-highlight"
            style={{
              background: 'var(--success-dim)',
              color: 'var(--text-primary)',
              border: '1px solid rgba(0,196,140,0.45)',
              borderRadius: 4,
              padding: '0 3px',
              boxShadow: '0 0 0 3px rgba(0,196,140,0.12)',
            }}
          >
            {target}
          </mark>
          {child.slice(idx + target.length)}
        </>
      )
    }

    if (Array.isArray(child)) {
      return child.map((item, index) => <span key={`${key}-${index}`}>{visit(item, `${key}-${index}`)}</span>)
    }

    return child
  }

  return visit(children)
}
// function renderContent(text) {
//   if (!text) return null
//   return text.split('\n\n').map((para, i) => {
//     if (!para.trim()) return null
//     const parts = para.split(/\*\*([^*]+)\*\*/g)
//     return (
//       <p key={i} style={{ marginBottom: '0.85rem', fontSize: '0.875rem', lineHeight: 1.85, color: 'var(--text-secondary)' }}>
//         {parts.map((part, j) =>
//           j % 2 === 1
//             ? <strong key={j} style={{ color: 'var(--text-primary)', fontWeight: 500 }}>{part}</strong>
//             : part
//         )}
//       </p>
//     )
//   })
// }

function SectionNavItem({ section, isActive, status, onClick }) {
  const statusColors = { approve: 'var(--success)', revise: 'var(--warning)', reject: 'var(--danger)' }
  return (
    <button
      onClick={onClick}
      style={{
        width: '100%', padding: '9px 12px', display: 'flex', alignItems: 'center',
        gap: 8, background: isActive ? 'var(--accent-glow)' : 'transparent',
        border: `1px solid ${isActive ? 'var(--accent-dim)' : 'transparent'}`,
        borderRadius: 'var(--radius-md)', cursor: 'pointer', textAlign: 'left',
        marginBottom: 2, transition: 'all 0.15s',
      }}
      onMouseEnter={e => { if (!isActive) e.currentTarget.style.background = 'var(--bg-hover)' }}
      onMouseLeave={e => { if (!isActive) e.currentTarget.style.background = 'transparent' }}
    >
      <div style={{
        width: 6, height: 6, borderRadius: '50%', flexShrink: 0,
        background: status ? statusColors[status] : isActive ? 'var(--accent)' : 'var(--border-mid)',
      }} />
      <div style={{ flex: 1, overflow: 'hidden' }}>
        <div style={{
          fontSize: 12, color: isActive ? 'var(--accent-text)' : 'var(--text-secondary)',
          fontWeight: isActive ? 500 : 400, whiteSpace: 'nowrap',
          overflow: 'hidden', textOverflow: 'ellipsis',
        }}>
          {section.title}
        </div>
        <div style={{ fontSize: 10, color: 'var(--text-muted)' }}>{section.word_count}w</div>
      </div>
    </button>
  )
}

export default function DocumentViewer({ result, highlightedSection }) {
  const { sections, setSections,activeSectionIdx, setActiveSectionIdx, feedbackLog } = useAppStore()
  const [copiedId, setCopiedId] = useState(null)
  const highlightedTarget = typeof highlightedSection === 'string'
    ? { sectionId: highlightedSection }
    : highlightedSection
  const highlightedSectionId = highlightedTarget?.sectionId
  const highlightedText = highlightedTarget?.value

  
  useEffect(() => {
    if (result?.sections && sections.length === 0) { // && sections.length === 0
      console.log(result.sections)
      setSections(result.sections)
      
    }
  }, [result])
//   useEffect(() => {
//   if (result?.sections) {
//     console.log(result.sections); // For debugging purposes
//     onFilled(result.sections);
//   }
// }, [result]);
  
useEffect(() => {
    if (activeSectionIdx >= sections.length) {
      setActiveSectionIdx(0)  // Go to the first section if current index is invalid
    }
  }, [sections])
  const currentSections = sections?.length ? sections : result?.sections || []
  const section = currentSections[activeSectionIdx]|| {}
  
  useEffect(() => {
    const updatedIndex = currentSections.findIndex(s => s.revised)

    if (updatedIndex !== -1 && updatedIndex !== activeSectionIdx) {
      setActiveSectionIdx(updatedIndex)
    }
  }, [sections])
  useEffect(() => {
  if (!highlightedSection) return
  const el = document.getElementById(`section-anchor-${highlightedSectionId}`)
  if (el) el.scrollIntoView({ behavior: 'smooth', block: 'start' })
  window.setTimeout(() => {
    const mark = el?.querySelector?.('.placeholder-fill-highlight')
    if (mark) mark.scrollIntoView({ behavior: 'smooth', block: 'center' })
  }, 80)
}, [highlightedSection, highlightedSectionId])
   
  const copySection = async (id, content) => {
    await navigator.clipboard.writeText(content)
    setCopiedId(id)
    setTimeout(() => setCopiedId(null), 1800)
  }

  const getSectionStatus = (sectionId) => {
    const fb = feedbackLog.findLast(f => f.section_id === sectionId)
    return fb?.action
  }

  const avgConf = currentSections.length
    ? Math.round(currentSections.reduce((s, sec) => s + (sec.confidence_score || 0), 0) / currentSections.length * 100)
    : 0

  return (
    <div style={{ display: 'flex', gap: 16, height: '100%' }}>
      {/* Section nav */}
      <div style={{
        width: 200, flexShrink: 0, display: 'flex', flexDirection: 'column', gap: 4,
      }}>
        {/* Mini stats */}
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 6, marginBottom: 8 }}>
          <div style={{ background: 'var(--bg-elevated)', borderRadius: 8, padding: '8px 10px', textAlign: 'center' }}>
            <div style={{ fontSize: 18, fontWeight: 600, color: 'var(--accent)' }}>{sections.length}</div>
            <div style={{ fontSize: 10, color: 'var(--text-muted)' }}>sections</div>
          </div>
          <div style={{ background: 'var(--bg-elevated)', borderRadius: 8, padding: '8px 10px', textAlign: 'center' }}>
            <div style={{ fontSize: 18, fontWeight: 600, color: 'var(--info)' }}>{avgConf}%</div>
            <div style={{ fontSize: 10, color: 'var(--text-muted)' }}>confidence</div>
          </div>
        </div>

        <div style={{ fontSize: 10, fontWeight: 600, color: 'var(--text-muted)', letterSpacing: '0.08em', textTransform: 'uppercase', padding: '0 4px', marginBottom: 4 }}>
          Sections
        </div>

        {currentSections.map((sec, i) => (
          <SectionNavItem
            key={sec.section_id}
            section={sec}
            isActive={i === activeSectionIdx}
            status={getSectionStatus(sec.section_id)}
            onClick={() => setActiveSectionIdx(i)}
          />
        ))}
      </div>

      {/* Content area */}
      <div style={{ flex: 1, overflow: 'auto' }}>
        {section && (
          <div className="animate-in">
            {/* Section header */}
            <div style={{
              display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between',
              marginBottom: 16, gap: 12,
            }}>
              <div>
                <h2 style={{ fontFamily: 'var(--font-display)', fontSize: 18, color: 'var(--text-primary)', marginBottom: 4 }}>
                  {section.title}
                </h2>
                <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap', alignItems: 'center' }}>
                  <Badge color="info" size="xs">
                    {Math.round((section.confidence_score || 0) * 100)}% confidence
                  </Badge>
                  <Badge color="default" size="xs">{section.word_count} words</Badge>
                  {section.revised && <Badge color="warning" size="xs">Edited</Badge>}
                  {section.sources_used?.length > 0 && (
                    <Badge color="default" size="xs">
                      {section.sources_used.length} source{section.sources_used.length !== 1 ? 's' : ''}
                    </Badge>
                  )}
                  {getSectionStatus(section.section_id) && (
                    <Badge color={
                      getSectionStatus(section.section_id) === 'approve' ? 'success' :
                      getSectionStatus(section.section_id) === 'revise' ? 'warning' : 'danger'
                    } size="xs">
                      {getSectionStatus(section.section_id)}d
                    </Badge>
                  )}
                </div>
              </div>
              <button
                onClick={() => copySection(section.section_id, section.content)}
                style={{
                  display: 'flex', alignItems: 'center', gap: 5,
                  background: 'var(--bg-elevated)', border: '1px solid var(--border-soft)',
                  borderRadius: 'var(--radius-sm)', padding: '5px 10px',
                  fontSize: 11, color: 'var(--text-secondary)', cursor: 'pointer',
                  flexShrink: 0, transition: 'all 0.15s',
                }}>
                {copiedId === section.section_id
                  ? <><Check size={12} color="var(--success)" /> Copied</>
                  : <><Copy size={12} /> Copy</>}
              </button>
            </div>

            {/* Content */}
            <div id={`section-anchor-${section.section_id}`}>
              <Card style={{
                marginBottom: 12,
                transition: 'box-shadow 0.4s, border-color 0.4s',
                ...(highlightedSectionId === section.section_id ? {
                  borderColor: 'var(--accent)',
                  boxShadow: '0 0 0 3px var(--accent-glow)',
                } : {}),
              }}>
            <Card style={{ marginBottom: 12 }}>
              <div className="prose" style={{ maxHeight: '55vh', overflowY: 'auto', paddingRight: 4 }}>
                <ReactMarkdown
                  remarkPlugins={[remarkGfm]}
                  components={{
                    table: ({ children }) => (
                      <table style={{
                        width: '100%',
                        borderCollapse: 'collapse',
                        marginBottom: '1rem'
                      }}>
                        {children}
                      </table>
                    ),
                    p: ({ children }) => (
                      <p>
                        {highlightedSectionId === section.section_id ? highlightFilledText(children, highlightedText) : children}
                      </p>
                    ),
                    li: ({ children }) => (
                      <li>
                        {highlightedSectionId === section.section_id ? highlightFilledText(children, highlightedText) : children}
                      </li>
                    ),
                    th: ({ children }) => (
                      <th style={{
                        border: '1px solid #ddd',
                        padding: '8px',
                        background: '#f5f5f5c1'
                      }}>
                        {highlightedSectionId === section.section_id ? highlightFilledText(children, highlightedText) : children}
                      </th>
                    ),
                    td: ({ children }) => (
                      <td style={{
                        border: '1px solid #ddd',
                        padding: '8px'
                      }}>
                        {highlightedSectionId === section.section_id ? highlightFilledText(children, highlightedText) : children}
                      </td>
                    )
                  }}
                >
                  {section.content}
                </ReactMarkdown>
              </div>
            </Card>
              </Card>
          </div>

            {/* Sources */}
            {section.sources_used?.length > 0 && (
              <div style={{ fontSize: 11, color: 'var(--text-muted)', display: 'flex', gap: 6, flexWrap: 'wrap' }}>
                <span>Sources:</span>
                {section.sources_used.map((src, i) => (
                  <span key={i} style={{
                    background: 'var(--bg-elevated)', padding: '1px 6px', borderRadius: 4,
                    border: '1px solid var(--border-subtle)',
                  }}>
                    {src}
                  </span>
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  )
}
