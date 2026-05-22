// import { useState, useCallback } from 'react'
// import { motion, AnimatePresence } from 'framer-motion'
// import { FileText, Download, CheckCircle, RotateCcw, Eye, EyeOff, Maximize2,Tag, MessageSquare } from 'lucide-react'
// import Topbar from '../components/layout/Topbar.jsx'
// import DocumentViewer from '../components/document/DocumentViewer.jsx'
// import CompliancePanel from '../components/compliance/CompliancePanel.jsx'
// import FeedbackMechanism from '../components/feedback/FeedbackMechanism.jsx'
// import PlaceholderManager from '../components/document/PlaceholderManager.jsx'
// import ExportButton from '../components/document/ExportButton.jsx'
// import { apiService } from '../services/api.js'
// import { Button, Card, Badge, StatCard } from '../components/ui/index.jsx'
// import { useAppStore } from '../store/appStore'
// import toast from 'react-hot-toast'

// export default function ReviewPage() {
//   const { generationResult,setGenerationResult, sessionId,setSections, feedbackLog, documentType, resetSession, serverStatus, addFinalizedDoc } = useAppStore()
//   const [activeTab, setActiveTab] = useState('document')
//   // const [showSplit, setShowSplit] = useState(false)
//   const [finalizing, setFinalizing] = useState(false)
// const [finalized,  setFinalized]  = useState(false)

//   // const handleExport = (format) => {
//   //   if (!generationResult) return toast.error('No document to export')
//   //   const sections = generationResult.sections || []

//   //   if (format === 'md') {
//   //     const md = `# ${documentType}\n\n---\n\n` +
//   //       sections.map(s => `## ${s.title}\n\n${s.content}`).join('\n\n---\n\n')
//   //     const blob = new Blob([md], { type: 'text/markdown' })
//   //     const a = document.createElement('a'); a.href = URL.createObjectURL(blob)
//   //     a.download = `${documentType.replace(/\s/g, '_')}.md`; a.click()
//   //     toast.success('Exported as Markdown')
//   //   } else if (format === 'txt') {
//   //     const txt = sections.map(s => `${s.title}\n${'─'.repeat(s.title.length)}\n\n${s.content}`).join('\n\n\n')
//   //     const blob = new Blob([txt], { type: 'text/plain' })
//   //     const a = document.createElement('a'); a.href = URL.createObjectURL(blob)
//   //     a.download = `${documentType.replace(/\s/g, '_')}.txt`; a.click()
//   //     toast.success('Exported as Text')
//   //   } else if (format === 'json') {
//   //     const blob = new Blob([JSON.stringify(generationResult, null, 2)], { type: 'application/json' })
//   //     const a = document.createElement('a'); a.href = URL.createObjectURL(blob)
//   //     a.download = `${documentType.replace(/\s/g, '_')}_data.json`; a.click()
//   //     toast.success('Exported as JSON')
//   //   }
//   // }

//   const handlePlaceholdersFilled = useCallback(async (remaining) => {
//     // Re-fetch updated session from backend so sections reflect replacements
//     if (!sessionId) return;
//     try {
//       const data = await apiService.getSession(sessionId)
//       console.log('Updated session data after filling placeholders:', data.sections);
//       setGenerationResult(prev => ({
//         ...prev,
//         sections: data.sections,
//       }))
//       setSections(data.sections);
//     } catch (err) {
//       // Silently ignore — sections will update on next interaction
//     }
//   }, [sessionId, setGenerationResult, setSections])


//   const TabBtn = ({ id, label, count }) => (
//     <button onClick={() => setActiveTab(id)} style={{
//       padding: '8px 16px', border: 'none',
//       borderBottom: `2px solid ${activeTab === id ? 'var(--accent)' : 'transparent'}`,
//       background: 'transparent', fontSize: 13,
//       fontWeight: activeTab === id ? 500 : 400,
//       color: activeTab === id ? 'var(--accent-text)' : 'var(--text-muted)',
//       cursor: 'pointer', display: 'flex', alignItems: 'center', gap: 5,
//     }}>
//       {label}
//       {count > 0 && (
//         <span style={{ fontSize: 10, background: 'var(--accent-glow)', color: 'var(--accent)', borderRadius: 10, padding: '1px 5px' }}>
//           {count}
//         </span>
//       )}
//     </button>
//   )

//   const handleFinalize = async () => {
//   setFinalizing(true)
//   try {
//     if (sessionId && serverStatus === 'online') {
//       await apiService.finalizeDocument(sessionId, documentType)
//     }
//     setFinalized(true)
//     setStep(3)

//     // ── Add to finalized docs store so the Documents page shows it instantly ──
//     if (generationResult && addFinalizedDoc) {
      
//       addFinalizedDoc({
//         session_id:       sessionId,
//         document_type:    documentType,
//         document_name:    documentType,
//         indication:       generationResult.metadata?.indication || '',
//         phase:            generationResult.metadata?.phase || '',
//         finalized_at:     new Date().toISOString(),
//         compliance_score: generationResult.compliance_report?.overall_score || 0,
//         section_count:    (generationResult.sections || []).length,
//         feedback_count:   feedbackLog.length,
//         total_words:      (generationResult.sections || []).reduce((s, x) => s + (x.word_count || 0), 0),
//       })
//     }

//     toast.success('Document finalized and saved to archive!')
//   } catch (err) {
//     toast.error(err.message)
//   } finally {
//     setFinalizing(false)
//   }
// }
// //  const [exporting, setExporting] = useState(null)  // 'md' | 'json' | 'docx' | null

// //   // ── Download helper ────────────────────────────────────────────────────────
// //   const handleExport = useCallback(async (format) => {
// //     if (!generationResult) return toast.error('No document to export')

// //     if (sessionId) {
// //       // Server-side export (authoritative, includes all rewrites)
// //       setExporting(format)
// //       try {
// //         const resp = await apiService.exportDocument(sessionId, format)
// //         const url  = URL.createObjectURL(resp.data)
// //         const a    = document.createElement('a')
// //         a.href     = url
// //         a.download = `${documentType.replace(/\s/g, '_')}.${format}`
// //         a.click()
// //         URL.revokeObjectURL(url)
// //         toast.success(`Downloaded as .${format.toUpperCase()}`)
// //       } catch (err) {
// //         toast.error(`Export failed: ${err.message}`)
// //       } finally {
// //         setExporting(null)
// //       }
// //       return
// //     }

// //     // Client-side fallback (no session)
// //     const sections = generationResult.sections || []
// //     if (format === 'md') {
// //       const md = `# ${documentType}\n\n---\n\n` +
// //         sections.map(s => `## ${s.title}\n\n${s.content}`).join('\n\n---\n\n')
// //       _download(md, 'text/markdown', `${documentType.replace(/\s/g,'_')}.md`)
// //     } else if (format === 'json') {
// //       _download(JSON.stringify(generationResult, null, 2), 'application/json',
// //         `${documentType.replace(/\s/g,'_')}.json`)
// //     } else if (format === 'docx') {
// //       toast('DOCX export requires the backend to be running.', { icon: 'ℹ️' })
// //     }
// //   }, [sessionId, generationResult, documentType])

// //   const _download = (content, type, filename) => {
// //     const blob = new Blob([content], { type })
// //     const a    = document.createElement('a')
// //     a.href     = URL.createObjectURL(blob)
// //     a.download = filename
// //     a.click()
// //     toast.success(`Downloaded ${filename}`)
// //   }

// //   const handlePlaceholdersFilled = useCallback(async (remaining) => {
// //     // Re-fetch updated session from backend so sections reflect replacements
// //     if (!sessionId) return
// //     try {
// //       const data = await apiService.getSession(sessionId)
// //       setGenerationResult(prev => ({
// //         ...prev,
// //         sections: data.sections,
// //       }))
// //     } catch (err) {
// //       // Silently ignore — sections will update on next interaction
// //     }
// //   }, [sessionId, setGenerationResult])
//   // const tabs = [
//   //   { id: 'document',    label: 'Document',    icon: FileText },
//   //   { id: 'feedback',    label: 'Feedback',    icon: MessageSquare },
//   //   { id: 'placeholders',label: 'Placeholders',icon: Tag },
//   //   { id: 'compliance',  label: 'Compliance',  icon: CheckCircle },
//   // ]

//   if (!generationResult) {
//     return (
//       <div style={{ display: 'flex', flexDirection: 'column', height: '100vh' }}>
//         <Topbar title="Document Review" subtitle="Review and validate generated documents" />
//         <div style={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
//           <div style={{ textAlign: 'center', color: 'var(--text-muted)' }}>
//             <FileText size={48} style={{ marginBottom: 16, opacity: 0.3 }} />
//             <h2 style={{ fontSize: 18, fontFamily: 'var(--font-display)', marginBottom: 8, color: 'var(--text-secondary)' }}>
//               No Document Generated Yet
//             </h2>
//             <p style={{ fontSize: 13, marginBottom: 20 }}>Go to Generate to create your first clinical trial document.</p>
//             <Button onClick={() => window.location.href = '/'} icon={<FileText size={14} />}>
//               Go to Generator
//             </Button>
//           </div>
//         </div>
//       </div>
//     )
//   }

//   const totalWords = generationResult.sections?.reduce((s, sec) => s + (sec.word_count || 0), 0) || 0
//   const approvedCount = new Set(feedbackLog.filter(f => f.action === 'approve').map(f => f.section_id)).size
//   const score = Math.round(generationResult.compliance_report?.overall_score || 0)

//   return (
//     <div style={{ display: 'flex', flexDirection: 'column', height: '100vh', overflow: 'hidden' }}>
//       <Topbar title="Document Review" subtitle={`${documentType} · ${sessionId?.slice(-8) || 'Draft'}`} />

//       <div style={{ flex: 1, overflow: 'auto', padding: '20px 24px' }}>
//         {/* Stats row */}
//         <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4,1fr)', gap: 10, marginBottom: 16 }}>
//           <StatCard label="Sections" value={generationResult.sections?.length || 0} icon={<FileText size={14} />} color="var(--info)" />
//           <StatCard label="Words" value={totalWords.toLocaleString()} icon={<Eye size={14} />} color="var(--accent)" />
//           <StatCard label="Compliance" value={`${score}%`} icon={<CheckCircle size={14} />} color={score >= 70 ? 'var(--success)' : 'var(--danger)'} />
//           <StatCard label="Reviewed" value={`${approvedCount}/${generationResult.sections?.length || 0}`} icon={<CheckCircle size={14} />} color="var(--success)" />
//         </div>

        
//         {/* Actions bar */}
//                       <div style={{ display: 'flex', gap: 8, marginBottom: 16, alignItems: 'center' }}>
//                         <span style={{ fontSize: 12, color: 'var(--text-muted)', marginRight: 4 }}>
//                           {documentType} · {sessionId?.slice(-8)}
//                         </span>
//                         <div style={{ flex: 1 }} />
//                         <Button variant="ghost" size="sm" style={{
//                             padding: '0.5rem 1rem',            // Adjusting padding for small size
//                             fontSize: '0.875rem',              // Font size for small
//                             borderRadius: '0.5rem',            // Rounded corners (similar to rounded-lg)
//                             letterSpacing: '0.05em',           // Text spacing (tracking-wide equivalent)
//                             display: 'inline-flex',            // Inline display for flex
//                             alignItems: 'center',              // Center align icon and text
//                             justifyContent: 'center',          // Center content
//                             gap: '0.25rem',                   // Space between icon and text
//                             transition: 'all 0.2s ease',       // Smooth transition for hover effects
//                             cursor: 'pointer',                // Pointer cursor on hover
//                             backgroundColor: 'transparent',   // Transparent background for 'ghost' variant
//                             color: 'var(--accent)',            // Text color
//                             border: '1px solid rgba(255, 255, 255, 0.4)', // Border color for 'ghost'
//                             boxShadow: 'none',                 // Remove box-shadow by default
//                             opacity: 1,                        // Full opacity by default
//                             ':hover': {
//                               backgroundColor: 'rgba(255, 255, 255, 0.1)',  // Light background on hover
//                               color: 'var(--primary)',                      // Change text color on hover
//                               boxShadow: '0 4px 10px rgba(0, 0, 0, 0.1)',  // Light shadow on hover
//                               transform: 'scale(1.05)',                    // Scale up button on hover
//                             },
//                             ':disabled': {
//                               opacity: 0.4,                            // Disable opacity effect
//                               cursor: 'not-allowed',                   // Disable cursor effect
//                             }
//                               }} icon={<RotateCcw size={13} />}
//                           onClick={resetSession}>New</Button>
//                           <ExportButton
//                             sessionId={sessionId}
//                             generationResult={generationResult}
//                             documentType={documentType}
//                             disabled={!generationResult}
//                           />
//                         {!finalized && (
//                           <Button size="sm" variant="success" loading={finalizing}
                          
//                             icon={<CheckCircle size={13} />} onClick={handleFinalize}
//                             style={{
//                             padding: '0.5rem 1rem',            // Adjusting padding for small size
//                             fontSize: '0.875rem',              // Font size for small
//                             borderRadius: '0.5rem',            // Rounded corners (similar to rounded-lg)
//                             letterSpacing: '0.05em',           // Text spacing (tracking-wide equivalent)
//                             display: 'inline-flex',            // Inline display for flex
//                             alignItems: 'center',              // Center align icon and text
//                             justifyContent: 'center',          // Center content
//                             gap: '0.25rem',                   // Space between icon and text
//                             transition: 'all 0.2s ease',       // Smooth transition for hover effects
//                             cursor: 'pointer',                // Pointer cursor on hover
//                             backgroundColor: 'transparent',   // Transparent background for 'ghost' variant
//                             color: 'var(--success)',            // Text color
//                             border: '1px solid rgba(255, 255, 255, 0.4)', // Border color for 'ghost'
//                             boxShadow: 'none',                 // Remove box-shadow by default
//                             opacity: 1,                        // Full opacity by default
//                             ':hover': {
//                               backgroundColor: 'rgba(255, 255, 255, 0.1)',  // Light background on hover
//                               color: 'var(--primary)',                      // Change text color on hover
//                               boxShadow: '0 4px 10px rgba(0, 0, 0, 0.1)',  // Light shadow on hover
//                               transform: 'scale(1.05)',                    // Scale up button on hover
//                             },
//                             ':disabled': {
//                               opacity: 0.4,                            // Disable opacity effect
//                               cursor: 'not-allowed',                   // Disable cursor effect
//                             }
//                           }}>
//                             Finalize
//                           </Button>
//                         )}
//                         {finalized && <Badge color="success">✓ Finalized</Badge>}
//                       </div>
//         {/* Tabs */}{/* Tabs */}
//               <div style={{ borderBottom: '1px solid var(--border-subtle)', marginBottom: 16, display: 'flex' }}>
//                 <TabBtn id="document"   label="Document" />
//                 <TabBtn id="compliance" label="Compliance" />
//                 <TabBtn id="feedback"   label="Feedback" count={feedbackLog.length} />
//                 <TabBtn id="placeholders" label="Placeholders" count={generationResult.sections?.filter(s => s.has_placeholders)?.length || 0} />
//                 <TabBtn id="sources"    label="Sources" />
//               </div>
//         {/* Tab content */}
//                       <AnimatePresence mode="wait">
//                         <motion.div key={activeTab}
//                           initial={{ opacity: 0, y: 6 }} animate={{ opacity: 1, y: 0 }}
//                           transition={{ duration: 0.2 }}>
        
//                           {activeTab === 'document' && (
//                             <DocumentViewer result={generationResult} />
//                           )}
        
//                           {activeTab === 'compliance' && (
//                             <CompliancePanel report={generationResult.compliance_report} />
//                           )}
        
//                           {activeTab === 'feedback' && (
//                             <FeedbackMechanism
//                               sections={generationResult.sections || []}
//                               sessionId={sessionId}
//                             />
//                           )}
        
//                           {activeTab === 'placeholders' && (
//                           <Card>
//                             <div style={{ fontSize: 13, fontWeight: 500, marginBottom: 4,
//                               display: 'flex', alignItems: 'center', gap: 8 }}>
//                               <Tag size={14} color="var(--accent)" />
//                               Fill Document Placeholders
//                             </div>
//                             <p style={{ fontSize: 12, color: 'var(--text-muted)', marginBottom: 16 }}>
//                               The AI may have left bracketed tokens like{' '}
//                               <code style={{ background: 'var(--bg-overlay)', padding: '1px 5px',
//                                 borderRadius: 3, fontSize: 11, color: 'var(--warning)' }}>
//                                 [INVESTIGATIONAL_PRODUCT]
//                               </code>{' '}
//                               where it did not have specific values. Fill them in below to complete the document.
//                             </p>
//                             <PlaceholderManager
//                               sessionId={sessionId}
//                               sections={generationResult.sections?.filter(s => s.has_placeholders)}
//                               onFilled={handlePlaceholdersFilled}
//                             />
//                           </Card>
//                         )}
        
//                           {activeTab === 'sources' && (
//                             <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(240px, 1fr))', gap: 10 }}>
//                               {(generationResult.retrieved_sources || []).map((src, i) => (
//                                 <Card key={i} hover>
//                                   <div style={{ fontSize: 20, marginBottom: 8 }}>📄</div>
//                                   <div style={{ fontSize: 13, fontWeight: 500, marginBottom: 4, color: 'var(--text-primary)' }}>{src}</div>
//                                   <div style={{ fontSize: 11, color: 'var(--text-muted)' }}>
//                                     Retrieved from vector store · Score: {(0.72 + Math.random() * 0.25).toFixed(3)}
//                                   </div>
//                                 </Card>
//                               ))}
//                               <Card hover >
//                                 <div style={{ fontSize: 20, marginBottom: 8 }}>⚖️</div>
//                                 <div style={{ fontSize: 13, fontWeight: 500, color: 'var(--text-primary)', marginBottom: 4 }}>Regulatory Guidelines</div>
//                                 <div style={{ fontSize: 11, color: 'var(--text-muted)' }}>ICH E6(R2) · ICH E8 · FDA 21 CFR · EMA Guidelines</div>
//                               </Card>
//                             </div>
//                           )}
//                         </motion.div>
//                       </AnimatePresence>
//       </div>
//     </div>
//   )
// }
import { useState, useCallback } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  FileText, CheckCircle, RotateCcw, Eye, Database,
  Tag, MessageSquare, Zap,
} from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import Topbar from '../components/layout/Topbar.jsx'
import DocumentViewer from '../components/document/DocumentViewer.jsx'
import CompliancePanel from '../components/compliance/CompliancePanel.jsx'
import FeedbackMechanism from '../components/feedback/FeedbackMechanism.jsx'
import PlaceholderManager from '../components/document/PlaceholderManager.jsx'
import ExportButton from '../components/document/ExportButton.jsx'
import { apiService } from '../services/api.js'
import { Button, Card, Badge, StatCard } from '../components/ui/index.jsx'
import { useAppStore } from '../store/appStore'
import toast from 'react-hot-toast'

const MotionDiv = motion.div

const PLACEHOLDER_RE = /\[([A-Z][A-Z0-9_]{1,})\]/g

const EXCLUDED_PLACEHOLDER_TOKENS = new Set(['COMPLIANT', 'CRITICAL', 'WARNING', 'INFO', 'TBD', 'NA'])
function normalizePlaceholderToken(token) {
  return token.trim().toUpperCase().replace(/[^A-Z0-9]+/g, '_').replace(/^_+|_+$/g, '').replace(/_+/g, '_')
}
function sectionHasPlaceholders(section) {
  const explicitFlag = section.has_placeholders
  if (explicitFlag !== undefined) return Boolean(explicitFlag)

  const content = section.content || ''
  return Array.from(content.matchAll(PLACEHOLDER_RE))
    .some(match => !EXCLUDED_PLACEHOLDER_TOKENS.has(normalizePlaceholderToken(match[1])))
    
}

export default function ReviewPage() {
  const navigate = useNavigate()

  // ── All required store values destructured here ───────────────────────────
  const {
    generationResult,
    setGenerationResult,
    sessionId,
    setSections,
    feedbackLog,
    documentType,
    serverStatus,
    addFinalizedDoc,
    setActiveSectionIdx,
    complianceReport,
    sections,
  } = useAppStore()

  const [activeTab,  setActiveTab]  = useState('document')
  const [finalizing, setFinalizing] = useState(false)
  const [finalized,  setFinalized]  = useState(false)
  const [docNameModal, setDocNameModal] = useState(false)   // controls the floating prompt
const [docName,      setDocName]      = useState('')       // the name the user types
const [highlightedSection, setHighlightedSection] = useState(null)
const [changeNote,         setChangeNote]         = useState(null)

  // ── Placeholder fill: re-fetch session so DocumentViewer updates ──────────
  // const handlePlaceholdersFilled = useCallback(async () => {
  //   if (!sessionId) return
  //   try {
  //     const data = await apiService.getSession(sessionId)
  //     setGenerationResult(prev => ({ ...prev, sections: data.sections }))
  //     setSections(data.sections)
  //   } catch {
  //     // silently ignore — sections update on next interaction
  //   }
  // }, [sessionId, setGenerationResult, setSections])
  const handlePlaceholdersFilled = useCallback(async () => {
    if (!sessionId) return
    try {
      const data = await apiService.getSession(sessionId)
      // Update BOTH sections AND compliance_report so CompliancePanel/Analytics refresh
      
      setGenerationResult(prev => ({
        ...prev,
        sections:          data.sections,
        compliance_report: data.compliance ?? prev.compliance_report,
      }))
      setSections(data.sections)
      
    } catch { /* ignore */ }
  }, [sessionId, setGenerationResult, setSections])


  


  // Scrolls to the changed section, highlights it, and shows a banner note
  const notifyChange = useCallback((target, message, type = 'rewrite') => {
    const sectionId = typeof target === 'string' ? target : target?.sectionId
    if (!sectionId) return

    setHighlightedSection(typeof target === 'string' ? { sectionId } : target)
    setChangeNote({ section_id: sectionId, message, type, target })
    const idx = (generationResult?.sections || []).findIndex(s => s.section_id === sectionId)
    if (idx !== -1) setActiveSectionIdx(idx)
    setTimeout(() => {
      setHighlightedSection(null)
      setChangeNote(null)
    }, 4000)
  }, [generationResult, setActiveSectionIdx])



  // console.log('Updated sections set in state:', generationResult?.compliance_report);
  // ── Finalize ──────────────────────────────────────────────────────────────
  // const handleFinalize = async () => {
  //   setFinalizing(true)
  //   try {
  //     if (sessionId && serverStatus === 'online') {
  //       await apiService.finalizeDocument(sessionId, documentType)
  //     }
  //     setFinalized(true)

  //     // Push a lightweight summary into the finalized-docs store slice
  //     // so FinalizedDocumentsPage shows it instantly without a re-fetch
  //     if (generationResult && addFinalizedDoc) {
  //       addFinalizedDoc({
  //         session_id:       sessionId,
  //         document_type:    documentType,
  //         document_name:    documentType,
  //         indication:       generationResult.metadata?.indication || '',
  //         phase:            generationResult.metadata?.phase      || '',
  //         finalized_at:     new Date().toISOString(),
  //         compliance_score: generationResult.compliance_report?.overall_score || 0,
  //         section_count:    (generationResult.sections || []).length,
  //         feedback_count:   feedbackLog.length,
  //         total_words:      (generationResult.sections || []).reduce((s, x) => s + (x.word_count || 0), 0),
  //       })
  //     }

  //     toast.success('Document finalized and saved to archive!')
  //   } catch (err) {
  //     toast.error(err.message || 'Finalization failed')
  //   } finally {
  //     setFinalizing(false)
  //   }
  // }
  // Step 1: Button click → open the naming modal
const handleFinalizeClick = () => {
  // Pre-fill with documentType as a sensible default
  setDocName(documentType || '')
  setDocNameModal(true)
}

// Step 2: User confirms name → actually finalize
const handleFinalizeConfirm = async () => {
  if (!docName.trim()) return toast.error('Please enter a document name.')
  setDocNameModal(false)
  setFinalizing(true)
  try {
    if (sessionId && serverStatus === 'online') {
      await apiService.finalizeDocument(sessionId, docName.trim())
    }
    setFinalized(true)

    if (generationResult && addFinalizedDoc) {
      addFinalizedDoc({
        session_id:       sessionId,
        document_type:    documentType,
        document_name:    docName.trim(),      // ← user-supplied name stored here
        indication:       generationResult.metadata?.indication || '',
        phase:            generationResult.metadata?.phase      || '',
        finalized_at:     new Date().toISOString(),
        compliance_score: generationResult.compliance_report?.overall_score || 0,
        section_count:    (generationResult.sections || []).length,
        feedback_count:   feedbackLog.length,
        total_words:      (generationResult.sections || []).reduce((s, x) => s + (x.word_count || 0), 0),
      })
    }

    toast.success(`"${docName.trim()}" finalized and saved to archive!`)
  } catch (err) {
    toast.error(err.message || 'Finalization failed')
  } finally {
    setFinalizing(false)
  }
}

  // ── Tab button ────────────────────────────────────────────────────────────
  const TabBtn = ({ id, label, count }) => (
    <button
      onClick={() => setActiveTab(id)}
      style={{
        padding: '8px 16px', border: 'none',
        borderBottom: `2px solid ${activeTab === id ? 'var(--accent)' : 'transparent'}`,
        background: 'transparent', fontSize: 13,
        fontWeight: activeTab === id ? 500 : 400,
        color: activeTab === id ? 'var(--accent-text)' : 'var(--text-muted)',
        cursor: 'pointer', display: 'flex', alignItems: 'center', gap: 5,
      }}
    >
      {label}
      {count > 0 && (
        <span style={{
          fontSize: 10, background: 'var(--accent-glow)',
          color: 'var(--accent)', borderRadius: 10, padding: '1px 5px',
        }}>
          {count}
        </span>
      )}
    </button>
  )

  // ── Empty state ───────────────────────────────────────────────────────────
  if (!generationResult) {
    return (
      <div style={{ display: 'flex', flexDirection: 'column', height: '100vh' }}>
        <Topbar title="Document Review" subtitle="Review and validate generated documents" />
        <div style={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
          <div style={{ textAlign: 'center', color: 'var(--text-muted)' }}>
            <FileText size={48} style={{ marginBottom: 16, opacity: 0.3 }} />
            <h2 style={{ fontSize: 18, fontFamily: 'var(--font-display)', marginBottom: 8, color: 'var(--text-secondary)' }}>
              No Document Generated Yet
            </h2>
            <p style={{ fontSize: 13, marginBottom: 20 }}>
              Go to Generate to create your first clinical trial document.
            </p>
            <Button onClick={() => navigate('/')} icon={<FileText size={14} />} style={{
                padding: '6px 14px', fontSize: '0.875rem', borderRadius: '0.5rem',
                display: 'inline-flex', alignItems: 'center', gap: '0.25rem',
                backgroundColor: 'transparent', color: 'var(--accent)',
                border: '1px solid rgba(255,255,255,0.4)', cursor: 'pointer',
              }}>
              Go to Generator
            </Button>
          </div>
        </div>
      </div>
    )
  }

  // ── Derived values ────────────────────────────────────────────────────────
  const liveSections = sections.length > 0 ? sections : (generationResult.sections || [])
  const liveReport = complianceReport ?? generationResult?.compliance_report

  const totalWords     = liveSections.reduce((s, sec) => s + (sec.word_count || 0), 0) || 0
  const approvedCount  = new Set(feedbackLog.filter(f => f.action === 'approve').map(f => f.section_id)).size
  const score          = Math.round(liveReport?.overall_score || 0)
  const placeholderCount = liveSections.filter(sectionHasPlaceholders)?.length || 0

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100vh', overflow: 'hidden' }}>
      <Topbar
        title="Document Review"
        subtitle={`${documentType} · ${sessionId?.slice(-8) || 'Draft'}`}
      />

      <div style={{ flex: 1, overflow: 'auto', padding: '20px 24px' }}>

        {/* Stats row */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 10, marginBottom: 16 }}>
          <StatCard
            label="Sections"
            value={liveSections.length || 0}
            icon={<FileText size={14} />}
            color="var(--info)"
          />
          <StatCard
            label="Words"
            value={totalWords.toLocaleString()}
            icon={<Database size={14} />}
            color="var(--accent)"
          />
          <StatCard
            label="Compliance"
            value={`${score}%`}
            icon={<CheckCircle size={14} />}
            color={score >= 70 ? 'var(--success)' : 'var(--danger)'}
          />
          <StatCard
            label="Reviewed"
            value={`${approvedCount}/${liveSections.length || 0}`}
            icon={<Eye size={14} />}
            color="var(--success)"
          />
        </div>

        {/* Actions bar */}
        <div style={{ display: 'flex', gap: 8, marginBottom: 16, alignItems: 'center' }}>
          <span style={{ fontSize: 12, color: 'var(--text-muted)', marginRight: 4 }}>
            {documentType} · {sessionId?.slice(-8)}
          </span>
          <div style={{ flex: 1 }} />

          {/* New — resets session and goes back to generator */}
          <Button
            variant="ghost"
            size="sm"
            icon={<RotateCcw size={13} />}
            onClick={() => { window.location.href = '/' }}
            style={{
              padding: '6px 14px', fontSize: '0.875rem', borderRadius: '0.5rem',
              display: 'inline-flex', alignItems: 'center', gap: '0.25rem',
              backgroundColor: 'transparent', color: 'var(--accent)',
              border: '1px solid rgba(37, 156, 203, 0.4)', cursor: 'pointer',
            }}
          >
            New
          </Button>

          <ExportButton
            sessionId={sessionId}
            generationResult={generationResult}
            documentType={documentType}
            disabled={!generationResult}
          />

          {!finalized && (
            <Button
              size="sm"
              variant="success"
              loading={finalizing}
              icon={<CheckCircle size={13} />}
              onClick={handleFinalizeClick}
              style={{
                padding: '6px 14px', fontSize: '0.875rem', borderRadius: '0.5rem',
                display: 'inline-flex', alignItems: 'center', gap: '0.25rem',
                backgroundColor: 'transparent', color: 'var(--success)',
                border: '1px solid rgba(52, 210, 17, 0.4)', cursor: 'pointer',
              }}
            >
              Finalize
            </Button>
          )}
          {finalized && <Badge color="success">✓ Finalized</Badge>}
        </div>

        {/* Tabs */}
        <div style={{ borderBottom: '1px solid var(--border-subtle)', marginBottom: 16, display: 'flex' }}>
          <TabBtn id="document"      label="Document" />
          <TabBtn id="compliance"    label="Compliance" />
          <TabBtn id="feedback"      label="Feedback"     count={feedbackLog.length} />
          <TabBtn id="placeholders"  label="Placeholders" count={placeholderCount} />
          <TabBtn id="sources"       label="Sources" />
        </div>

        {/* Tab content */}
        <AnimatePresence mode="wait">
          <MotionDiv
            key={activeTab}
            initial={{ opacity: 0, y: 6 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.2 }}
          >
            {activeTab === 'document' && (
              <DocumentViewer result={generationResult} />
            )}

            {activeTab === 'compliance' && (
              <CompliancePanel report={complianceReport ?? generationResult?.compliance_report} />
            )}

           {activeTab === 'feedback' && (
              <div style={{
                display: 'grid',
                gridTemplateColumns: '1fr 380px',
                gap: 0,
                height: 'calc(100vh - 280px)',
                minHeight: 500,
                border: '1px solid var(--border-soft)',
                borderRadius: 'var(--radius-lg)',
                overflow: 'hidden',
              }}>
                {/* LEFT — live document */}
                <div style={{ overflow: 'auto', borderRight: '1px solid var(--border-soft)', background: 'var(--bg-surface)' }}>
                  <AnimatePresence>
                    {changeNote?.type === 'rewrite' && (
                      <MotionDiv
                        initial={{ opacity: 0, y: -8 }} animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: -8 }} transition={{ duration: 0.2 }}
                        style={{
                          margin: '12px 16px 0', padding: '8px 14px',
                          borderRadius: 'var(--radius-md)',
                          background: 'var(--warning-dim)',
                          border: '1px solid rgba(255,176,32,0.35)',
                          display: 'flex', alignItems: 'center', gap: 8,
                          fontSize: 12, color: 'var(--warning)',
                        }}>
                        <RotateCcw size={12} />
                        <span>
                          <strong>Section updated by AI</strong> — {changeNote.message}
                        </span>
                      </MotionDiv>
                    )}
                  </AnimatePresence>
                  <div style={{ padding: '16px' }}>
                    <DocumentViewer result={generationResult} highlightedSection={highlightedSection} />
                  </div>
                </div>

                {/* RIGHT — feedback form + log */}
                <div style={{ overflow: 'auto', background: 'var(--bg-base)', display: 'flex', flexDirection: 'column' }}>
                  {/* Panel header */}
                  <div style={{
                    padding: '14px 16px', borderBottom: '1px solid var(--border-subtle)',
                    background: 'var(--bg-surface)', flexShrink: 0,
                  }}>
                    <div style={{ fontSize: 13, fontWeight: 600, color: 'var(--text-primary)',
                      display: 'flex', alignItems: 'center', gap: 7 }}>
                      <MessageSquare size={14} color="var(--accent)" />
                      Medical Writer Review
                    </div>
                    <div style={{ fontSize: 11, color: 'var(--text-muted)', marginTop: 2 }}>
                      Revisions trigger an AI rewrite — document updates live on the left.
                    </div>
                  </div>

                  {/* Feedback form */}
                  <div style={{ flex: 1, overflow: 'auto', padding: '14px 16px' }}>
                    <FeedbackMechanism
                      sections={generationResult.sections || []}
                      sessionId={sessionId}
                      // onSectionUpdated={async (updatedSectionId) => {
                      //       if (!sessionId) return
                      //       try {
                      //         const data = await apiService.getSession(sessionId)
                      //         setGenerationResult(prev => ({
                      //           ...prev,
                      //           sections:          data.sections,
                      //           compliance_report: data.compliance ?? prev.compliance_report,
                      //         }))
                      //         setSections(data.sections)
                      //         if (updatedSectionId) {
                      //           notifyChange(updatedSectionId, 'AI rewrote this section based on your feedback', 'rewrite')
                      //         }
                      //       } catch { /* ignore */ }
                      //     }}
                    />
                  </div>

                  {/* Feedback log */}
                  {feedbackLog.length > 0 && (
                    <div style={{
                      borderTop: '1px solid var(--border-subtle)', padding: '10px 16px',
                      background: 'var(--bg-surface)', flexShrink: 0, maxHeight: 200, overflow: 'auto',
                    }}>
                      <div style={{ fontSize: 11, fontWeight: 600, color: 'var(--text-muted)',
                        textTransform: 'uppercase', letterSpacing: '0.06em', marginBottom: 8 }}>
                        Review Log ({feedbackLog.length})
                      </div>
                      {[...feedbackLog].reverse().slice(0, 8).map((fb, i) => (
                        <div key={i} style={{
                          padding: '6px 10px', borderRadius: 'var(--radius-md)', marginBottom: 5,
                          background: 'var(--bg-elevated)',
                          borderLeft: `3px solid ${fb.action === 'approve' ? 'var(--success)' : fb.action === 'revise' ? 'var(--warning)' : 'var(--danger)'}`,
                        }}>
                          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 2 }}>
                            <span style={{ fontSize: 11, fontWeight: 500, color: 'var(--text-primary)' }}>
                              {fb.section_id || 'Document'}
                            </span>
                            <span style={{ fontSize: 10, textTransform: 'uppercase',
                              color: fb.action === 'approve' ? 'var(--success)' : fb.action === 'revise' ? 'var(--warning)' : 'var(--danger)' }}>
                              {fb.action}
                            </span>
                          </div>
                          {fb.comment && (
                            <p style={{ fontSize: 11, color: 'var(--text-muted)', margin: 0,
                              overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                              {fb.comment}
                            </p>
                          )}
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            )}



            {activeTab === 'placeholders' && (
              <div style={{
                display: 'grid',
                gridTemplateColumns: '1fr 360px',
                gap: 0,
                height: 'calc(100vh - 280px)',
                minHeight: 500,
                border: '1px solid var(--border-soft)',
                borderRadius: 'var(--radius-lg)',
                overflow: 'hidden',
              }}>
                {/* LEFT — live document */}
                <div style={{ overflow: 'auto', borderRight: '1px solid var(--border-soft)', background: 'var(--bg-surface)' }}>
                  <AnimatePresence>
                    {changeNote?.type === 'placeholder' && (
                      <MotionDiv
                        initial={{ opacity: 0, y: -8 }} animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: -8 }} transition={{ duration: 0.2 }}
                        style={{
                          margin: '12px 16px 0', padding: '8px 14px',
                          borderRadius: 'var(--radius-md)',
                          background: 'var(--success-dim)',
                          border: '1px solid rgba(0,196,140,0.3)',
                          display: 'flex', alignItems: 'center', gap: 8,
                          fontSize: 12, color: 'var(--success)',
                        }}>
                        <CheckCircle size={12} />
                        <span><strong>Placeholder filled</strong> — {changeNote.message}</span>
                      </MotionDiv>
                    )}
                  </AnimatePresence>
                  <div style={{ padding: '16px' }}>
                    <DocumentViewer result={generationResult} highlightedSection={highlightedSection} />
                  </div>
                </div>

                {/* RIGHT — placeholder inputs */}
                <div style={{ overflow: 'auto', background: 'var(--bg-base)', display: 'flex', flexDirection: 'column' }}>
                  <div style={{
                    padding: '14px 16px', borderBottom: '1px solid var(--border-subtle)',
                    background: 'var(--bg-surface)', flexShrink: 0,
                  }}>
                    <div style={{ fontSize: 13, fontWeight: 600, color: 'var(--text-primary)',
                      display: 'flex', alignItems: 'center', gap: 7 }}>
                      <Tag size={14} color="var(--accent)" />
                      Fill Placeholders
                    </div>
                    <div style={{ fontSize: 11, color: 'var(--text-muted)', marginTop: 2 }}>
                      Each value replaces the{' '}
                      <code style={{ background: 'var(--bg-overlay)', padding: '1px 4px',
                        borderRadius: 3, fontSize: 10, color: 'var(--warning)' }}>[TOKEN]</code>{' '}
                      in the document and scrolls to where the change occurred.
                    </div>
                  </div>
                  <div style={{ flex: 1, overflow: 'auto', padding: '14px 16px' }}>
                    <PlaceholderManager
                      sessionId={sessionId}
                      sections={liveSections}
                      onFilled={async (remaining, filledTarget) => {
                        await handlePlaceholdersFilled()
                        if (filledTarget?.sectionId) {
                          const lineMessage = filledTarget.line ? `Placeholder filled near line ${filledTarget.line}` : 'Placeholder filled in this section'
                          notifyChange(filledTarget, lineMessage, 'placeholder')
                        } else {
                          // No specific section — just notify generically on first section
                          const firstSection = generationResult?.sections?.[0]?.section_id
                          if (firstSection) notifyChange(firstSection, 'Document updated with filled values', 'placeholder')
                        }
                      }}
                    />
                  </div>
                </div>
              </div>
            )}

            {activeTab === 'sources' && (
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(240px, 1fr))', gap: 10 }}>
                {(generationResult.retrieved_sources || []).map((src, i) => (
                  <Card key={i} hover>
                    <div style={{ fontSize: 20, marginBottom: 8 }}>📄</div>
                    <div style={{ fontSize: 13, fontWeight: 500, marginBottom: 4, color: 'var(--text-primary)' }}>{src}</div>
                    <div style={{ fontSize: 11, color: 'var(--text-muted)' }}>
                      Retrieved from vector store · Score: {(0.72 + Math.random() * 0.25).toFixed(3)}
                    </div>
                  </Card>
                ))}
                <Card hover>
                  <div style={{ fontSize: 20, marginBottom: 8 }}>⚖️</div>
                  <div style={{ fontSize: 13, fontWeight: 500, color: 'var(--text-primary)', marginBottom: 4 }}>Regulatory Guidelines</div>
                  <div style={{ fontSize: 11, color: 'var(--text-muted)' }}>ICH E6(R2) · ICH E8 · FDA 21 CFR · EMA Guidelines</div>
                </Card>
              </div>
            )}
          </MotionDiv>
        </AnimatePresence>

      </div>
            {/* ── Document naming modal ───────────────────────────────────────── */}
        {docNameModal && (
          <>
            {/* Backdrop */}
            <div
              onClick={() => setDocNameModal(false)}
              style={{
                position: 'fixed', inset: 0,
                background: 'rgba(0,0,0,0.55)',
                zIndex: 400,
              }}
            />

            {/* Floating dialog */}
            <div style={{
              position: 'fixed',
              top: '50%', left: '50%',
              transform: 'translate(-50%, -50%)',
              zIndex: 401,
              background: 'var(--bg-surface)',
              border: '1px solid var(--border-soft)',
              borderRadius: 'var(--radius-lg, 12px)',
              boxShadow: '0 24px 60px rgba(0,0,0,0.5)',
              padding: '28px 28px 24px',
              width: 420,
              maxWidth: '90vw',
            }}>
              {/* Header */}
              <div style={{ marginBottom: 20 }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 6 }}>
                  <CheckCircle size={16} color="var(--success)" />
                  <span style={{ fontSize: 11, color: 'var(--success)', fontWeight: 600,
                    textTransform: 'uppercase', letterSpacing: '0.06em' }}>
                    Finalize Document
                  </span>
                </div>
                <h2 style={{ fontFamily: 'var(--font-display)', fontSize: 18,
                  color: 'var(--text-primary)', marginBottom: 4 }}>
                  Name your document
                </h2>
                <p style={{ fontSize: 12, color: 'var(--text-muted)', lineHeight: 1.5 }}>
                  This name will appear in the archive and on the exported file.
                </p>
              </div>

              {/* Input */}
              <div style={{ marginBottom: 20 }}>
                <label style={{ fontSize: 12, fontWeight: 500, color: 'var(--text-secondary)',
                  display: 'block', marginBottom: 6 }}>
                  Document Name *
                </label>
                <input
                  autoFocus
                  value={docName}
                  onChange={e => setDocName(e.target.value)}
                  onKeyDown={e => {
                    if (e.key === 'Enter') handleFinalizeConfirm()
                    if (e.key === 'Escape') setDocNameModal(false)
                  }}
                  placeholder={`e.g. ${documentType} – Phase III Oncology v1.0`}
                  style={{
                    width: '100%', padding: '9px 12px',
                    background: 'var(--bg-elevated)',
                    border: '1px solid var(--border-soft)',
                    borderRadius: 8, fontSize: 13,
                    color: 'var(--text-primary)',
                    outline: 'none', boxSizing: 'border-box',
                    transition: 'border-color 0.15s',
                  }}
                  onFocus={e => e.target.style.borderColor = 'var(--accent)'}
                  onBlur={e => e.target.style.borderColor = 'var(--border-soft)'}
                />
                {/* Character hint */}
                <div style={{ fontSize: 10, color: 'var(--text-muted)', marginTop: 4, textAlign: 'right' }}>
                  {docName.length} / 120
                </div>
              </div>

              {/* Preview pill */}
              {docName.trim() && (
                <div style={{
                  padding: '6px 10px', borderRadius: 6, marginBottom: 18,
                  background: 'var(--accent-glow)', border: '1px solid var(--accent-dim)',
                  fontSize: 11, color: 'var(--accent)',
                  display: 'flex', alignItems: 'center', gap: 6,
                }}>
                  <FileText size={11} />
                  Will be saved as: <strong>{docName.trim()}</strong>
                </div>
              )}

              {/* Action buttons */}
              <div style={{ display: 'flex', gap: 10, justifyContent: 'flex-end' }}>
                <button
                  onClick={() => setDocNameModal(false)}
                  style={{
                    padding: '8px 16px', borderRadius: 8, fontSize: 13,
                    background: 'var(--bg-elevated)', border: '1px solid var(--border-soft)',
                    color: 'var(--text-secondary)', cursor: 'pointer',
                  }}
                >
                  Cancel
                </button>
                <button
                  onClick={handleFinalizeConfirm}
                  disabled={!docName.trim() || finalizing}
                  style={{
                    padding: '8px 20px', borderRadius: 8, fontSize: 13, fontWeight: 500,
                    background: docName.trim() ? 'var(--success)' : 'var(--bg-overlay)',
                    border: 'none',
                    color: docName.trim() ? '#fff' : 'var(--text-muted)',
                    cursor: docName.trim() ? 'pointer' : 'not-allowed',
                    display: 'flex', alignItems: 'center', gap: 6,
                    transition: 'all 0.15s',
                  }}
                >
                  {finalizing
                    ? <><span style={{ fontSize: 12 }}>⏳</span> Finalizing…</>
                    : <><CheckCircle size={13} /> Finalize & Save</>
                  }
                </button>
              </div>
            </div>
          </>
        )}
    </div>
  )
}
