// import { useState, useEffect, useCallback } from 'react'
// import { useNavigate } from 'react-router-dom'
// import { motion, AnimatePresence } from 'framer-motion'
// import toast from 'react-hot-toast'
// import {
//   Zap, FileText, CheckCircle, ChevronRight,
//   RotateCcw, Download, Eye, Database, Tag
// } from 'lucide-react'
// import { useAppStore } from '../store/appStore'
// import { apiService } from '../services/api.js'
// import StudyMetadataForm from '../components/forms/StudyMetadataForm.jsx'
// import GenerationProgress from '../components/document/GenerationProgress.jsx'
// import DocumentViewer from '../components/document/DocumentViewer.jsx'
// // import CompliancePanel from '../components/compliance/CompliancePanel.jsx'
// // import FeedbackMechanism from '../components/feedback/FeedbackMechanism.jsx'
// // import PlaceholderManager from '../components/document/PlaceholderManager.jsx'
// // import ExportButton from '../components/document/ExportButton.jsx'
// import Topbar from '../components/layout/Topbar.jsx'
// import { Button, Badge, Card, StatCard } from '../components/ui/index.jsx'
// // import { set } from 'react-hook-form'

// const PIPELINE_STAGES = [0, 1, 2, 3, 4]
// const STAGE_DURATIONS = [800, 600, 400, 700, 500]

// function mockPipeline(setStage) {
//   return new Promise((resolve) => {
//     let s = 0
//     const next = () => {
//       setStage(s)
//       s++
//       if (s < PIPELINE_STAGES.length) setTimeout(next, STAGE_DURATIONS[s] || 600)
//       else setTimeout(resolve, 400)
//     }
//     next()
//   })
// }

// // const TABS = ['document', 'compliance', 'feedback', 'sources']

// export default function GeneratePage() {
//   const navigate = useNavigate()
//   const {
//     currentStep, setStep, setSections,
//     generationStage, setGenerationStage,
//     generationResult, setGenerationResult,
//     sessionId, setSessionId,
//     isGenerating, setIsGenerating,
//     documentType, setDocumentType,
//     resetSession, feedbackLog,
//     serverStatus,
//   } = useAppStore()

//   // const [activeTab, setActiveTab] = useState('document')
//   // const [finalizing, setFinalizing] = useState(false)
//   // const [finalized, setFinalized] = useState(false)
  
//   const handleGenerate = useCallback(async (formData) => {
//     setIsGenerating(true)
//     setStep(1)
//     setGenerationStage(-1)
//     setDocumentType(formData.document_type)

//     // Run pipeline stages animation
//     const pipelineP = mockPipeline(setGenerationStage)

//     try {
//       let result
//       if (serverStatus === 'online') {
//         // Real API call
//         const [apiResult] = await Promise.all([
//           apiService.generateDocument({
//             metadata: formData.metadata,
//             document_type: formData.document_type,
//             rag_top_k: formData.rag_top_k,
//             include_compliance_check: true,
//             additional_context: formData.additional_context,
//             model_tier: formData.model_tier,
//           }),
//           pipelineP,
//         ])
//         result = apiResult
//       } else {
//         // Mock result when API offline
//         await pipelineP
//         await new Promise(r => setTimeout(r, 600))
//         result = buildMockResult(formData)
//       }

//       setSessionId(result.session_id)
//       setGenerationResult(result)
//       setStep(2)
//       setFinalized(false)
//       toast.success(`${formData.document_type} generated!`)
//     } catch (err) {
//       toast.error(err.message || 'Generation failed')
//       setStep(0)
//     } finally {
//       setIsGenerating(false)
//       setGenerationStage(-1)
//     }
//   }, [serverStatus])

// //   const handleFinalize = async () => {
// //   setFinalizing(true)
// //   try {
// //     if (sessionId && serverStatus === 'online') {
// //       await apiService.finalizeDocument(sessionId, documentType)
// //     }
// //     setFinalized(true)
// //     setStep(3)

// //     // ── Add to finalized docs store so the Documents page shows it instantly ──
// //     if (generationResult) {
// //       const { addFinalizedDoc, feedbackLog: log } = useAppStore.getState()
// //       addFinalizedDoc({
// //         session_id:       sessionId,
// //         document_type:    documentType,
// //         document_name:    documentType,
// //         indication:       generationResult.metadata?.indication || '',
// //         phase:            generationResult.metadata?.phase || '',
// //         finalized_at:     new Date().toISOString(),
// //         compliance_score: generationResult.compliance_report?.overall_score || 0,
// //         section_count:    (generationResult.sections || []).length,
// //         feedback_count:   log.length,
// //         total_words:      (generationResult.sections || []).reduce((s, x) => s + (x.word_count || 0), 0),
// //       })
// //     }

// //     toast.success('Document finalized and saved to archive!')
// //   } catch (err) {
// //     toast.error(err.message)
// //   } finally {
// //     setFinalizing(false)
// //   }
// // }
//   // const handleExport = () => {
//   //   if (!generationResult) return
//   //   const sections = generationResult.sections || []
//   //   const md = sections.map(s => `## ${s.title}\n\n${s.content}`).join('\n\n---\n\n')
//   //   const blob = new Blob([md], { type: 'text/markdown' })
//   //   const a = document.createElement('a')
//   //   a.href = URL.createObjectURL(blob)
//   //   a.download = `${documentType.replace(/\s/g, '_')}_${sessionId || 'draft'}.md`
//   //   a.click()
//   //   toast.success('Exported to Markdown')
//   // }

// //   const handleExport = async (format) => {
// //   if (!generationResult) return toast.error('No document to export')
// //   setExporting(format)
// //   try {
// //     const blob = await apiService.exportDocument(sessionId, format)  // already a Blob
// //     const url  = URL.createObjectURL(blob)                           // ← no .data
// //     const a    = document.createElement('a')
// //     a.href     = url
// //     a.download = `${documentType.replace(/\s/g, '_')}.${format}`
// //     a.click()
// //     URL.revokeObjectURL(url)
// //     toast.success(`Downloaded .${format.toUpperCase()}`)
// //   } catch (err) {
// //     toast.error(`Export failed: ${err.message}`)
// //   } finally {
// //     setExporting(null)
// //   }
// // }
 

   
// // const handlePlaceholdersFilled = useCallback(async (remaining) => {
// //     // Re-fetch updated session from backend so sections reflect replacements
// //     if (!sessionId) return;
// //     try {
// //       const data = await apiService.getSession(sessionId)
// //       console.log('Updated session data after filling placeholders:', data.sections);
// //       setGenerationResult(prev => ({
// //         ...prev,
// //         sections: data.sections,
// //       }))
// //       setSections(data.sections);
// //     } catch (err) {
// //       // Silently ignore — sections will update on next interaction
// //     }
// //   }, [sessionId, setGenerationResult, setSections])
// //   const TabBtn = ({ id, label, count }) => (
// //     <button onClick={() => setActiveTab(id)} style={{
// //       padding: '8px 16px', border: 'none',
// //       borderBottom: `2px solid ${activeTab === id ? 'var(--accent)' : 'transparent'}`,
// //       background: 'transparent', fontSize: 13,
// //       fontWeight: activeTab === id ? 500 : 400,
// //       color: activeTab === id ? 'var(--accent-text)' : 'var(--text-muted)',
// //       cursor: 'pointer', display: 'flex', alignItems: 'center', gap: 5,
// //     }}>
// //       {label}
// //       {count > 0 && (
// //         <span style={{ fontSize: 10, background: 'var(--accent-glow)', color: 'var(--accent)', borderRadius: 10, padding: '1px 5px' }}>
// //           {count}
// //         </span>
// //       )}
// //     </button>
// //   )

//   // return (
//   //   <div style={{ display: 'flex', flexDirection: 'column', height: '100vh', overflow: 'hidden' }}>
//   //     <Topbar
//   //       title="Clinical Trial Document Generator"
//   //       subtitle="RAG-Powered · Groq LLM · ICH E6/E3 Compliant"
//   //     />

//   //     <div style={{ flex: 1, overflow: 'auto', padding: '20px 24px' }}>
//   //       {/* Step 0 — Form */}
//   //       <AnimatePresence mode="wait">
//   //         {currentStep === 0 && (
//   //           <motion.div key="form"
//   //             initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -8 }}
//   //             transition={{ duration: 0.3 }}
//   //             style={{ maxWidth: 720, margin: '0 auto' }}>

//   //             {/* Hero */}
//   //             <div style={{ marginBottom: 24, textAlign: 'center' }}>
//   //               <h1 style={{ fontFamily: 'var(--font-display)', fontSize: 28, marginBottom: 6, color: 'var(--text-primary)' }}>
//   //                 Generate Clinical Trial Documents
//   //               </h1>
//   //               <p style={{ fontSize: 14, color: 'var(--text-muted)', maxWidth: 480, margin: '0 auto' }}>
//   //                 AI-powered drafting with FAISS retrieval, Groq LLM generation, and automated compliance validation.
//   //               </p>
//   //               {serverStatus !== 'online' && (
//   //                 <div style={{ marginTop: 10, display: 'inline-flex', alignItems: 'center', gap: 6, fontSize: 12, color: 'var(--warning)', background: 'var(--warning-dim)', padding: '4px 12px', borderRadius: 20, border: '1px solid rgba(245,166,35,0.3)' }}>
//   //                   ⚠ API offline — using mock generation
//   //                 </div>
//   //               )}
//   //             </div>

//   //             <StudyMetadataForm onSubmit={handleGenerate} isLoading={isGenerating} />
//   //           </motion.div>
//   //         )}

//   //         {/* Step 1 — Progress */}
//   //         {currentStep === 1 && (
//   //           <motion.div key="progress"
//   //             initial={{ opacity: 0, scale: 0.97 }} animate={{ opacity: 1, scale: 1 }} exit={{ opacity: 0 }}
//   //             transition={{ duration: 0.3 }}
//   //             style={{ maxWidth: 560, margin: '0 auto' }}>
//   //             <GenerationProgress />
//   //           </motion.div>
//   //         )}

//   //         {/* Step 2+ — Review */}
//   //         {currentStep >= 2 && generationResult && (
//   //           <motion.div key="preview"
//   //             initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }}
//   //             transition={{ duration: 0.35 }}>

//   //             {/* Stats row */}
//   //             <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 10, marginBottom: 16 }}>
//   //               <StatCard
//   //                 label="Sections" icon={<FileText size={14} />}
//   //                 value={generationResult.sections?.length || 0}
//   //                 color="var(--info)"
//   //               />
//   //               <StatCard
//   //                 label="Total Words" icon={<Database size={14} />}
//   //                 value={(generationResult.total_words || generationResult.sections?.reduce((s, sec) => s + (sec.word_count || 0), 0) || 0).toLocaleString()}
//   //                 color="var(--accent)"
//   //               />
//   //               <StatCard
//   //                 label="Compliance" icon={<CheckCircle size={14} />}
//   //                 value={`${Math.round(generationResult.compliance_report?.overall_score || 0)}%`}
//   //                 color={generationResult.compliance_report?.is_compliant ? 'var(--success)' : 'var(--danger)'}
//   //               />
//   //               <StatCard
//   //                 label="RAG Sources" icon={<Zap size={14} />}
//   //                 value={generationResult.retrieved_sources?.length || 0}
//   //                 color="var(--info)"
//   //               />
//   //             </div>

//   //             {/* Actions bar */}
//   //             <div style={{ display: 'flex', gap: 8, marginBottom: 16, alignItems: 'center' }}>
//   //               <span style={{ fontSize: 12, color: 'var(--text-muted)', marginRight: 4 }}>
//   //                 {documentType} · {sessionId?.slice(-8)}
//   //               </span>
//   //               <div style={{ flex: 1 }} />
//   //               <Button variant="ghost" size="sm" style={{
//   //                   padding: '0.5rem 1rem',            // Adjusting padding for small size
//   //                   fontSize: '0.875rem',              // Font size for small
//   //                   borderRadius: '0.5rem',            // Rounded corners (similar to rounded-lg)
//   //                   letterSpacing: '0.05em',           // Text spacing (tracking-wide equivalent)
//   //                   display: 'inline-flex',            // Inline display for flex
//   //                   alignItems: 'center',              // Center align icon and text
//   //                   justifyContent: 'center',          // Center content
//   //                   gap: '0.25rem',                   // Space between icon and text
//   //                   transition: 'all 0.2s ease',       // Smooth transition for hover effects
//   //                   cursor: 'pointer',                // Pointer cursor on hover
//   //                   backgroundColor: 'transparent',   // Transparent background for 'ghost' variant
//   //                   color: 'var(--accent)',            // Text color
//   //                   border: '1px solid rgba(255, 255, 255, 0.4)', // Border color for 'ghost'
//   //                   boxShadow: 'none',                 // Remove box-shadow by default
//   //                   opacity: 1,                        // Full opacity by default
//   //                   ':hover': {
//   //                     backgroundColor: 'rgba(255, 255, 255, 0.1)',  // Light background on hover
//   //                     color: 'var(--primary)',                      // Change text color on hover
//   //                     boxShadow: '0 4px 10px rgba(0, 0, 0, 0.1)',  // Light shadow on hover
//   //                     transform: 'scale(1.05)',                    // Scale up button on hover
//   //                   },
//   //                   ':disabled': {
//   //                     opacity: 0.4,                            // Disable opacity effect
//   //                     cursor: 'not-allowed',                   // Disable cursor effect
//   //                   }
//   //                     }} icon={<RotateCcw size={13} />}
//   //                 onClick={resetSession}>New</Button>
//   //                 <ExportButton
//   //                   sessionId={sessionId}
//   //                   generationResult={generationResult}
//   //                   documentType={documentType}
//   //                   disabled={!generationResult}
//   //                 />
//   //               {!finalized && (
//   //                 <Button size="sm" variant="success" loading={finalizing}
                  
//   //                   icon={<CheckCircle size={13} />} onClick={handleFinalize}
//   //                   style={{
//   //                   padding: '0.5rem 1rem',            // Adjusting padding for small size
//   //                   fontSize: '0.875rem',              // Font size for small
//   //                   borderRadius: '0.5rem',            // Rounded corners (similar to rounded-lg)
//   //                   letterSpacing: '0.05em',           // Text spacing (tracking-wide equivalent)
//   //                   display: 'inline-flex',            // Inline display for flex
//   //                   alignItems: 'center',              // Center align icon and text
//   //                   justifyContent: 'center',          // Center content
//   //                   gap: '0.25rem',                   // Space between icon and text
//   //                   transition: 'all 0.2s ease',       // Smooth transition for hover effects
//   //                   cursor: 'pointer',                // Pointer cursor on hover
//   //                   backgroundColor: 'transparent',   // Transparent background for 'ghost' variant
//   //                   color: 'var(--success)',            // Text color
//   //                   border: '1px solid rgba(255, 255, 255, 0.4)', // Border color for 'ghost'
//   //                   boxShadow: 'none',                 // Remove box-shadow by default
//   //                   opacity: 1,                        // Full opacity by default
//   //                   ':hover': {
//   //                     backgroundColor: 'rgba(255, 255, 255, 0.1)',  // Light background on hover
//   //                     color: 'var(--primary)',                      // Change text color on hover
//   //                     boxShadow: '0 4px 10px rgba(0, 0, 0, 0.1)',  // Light shadow on hover
//   //                     transform: 'scale(1.05)',                    // Scale up button on hover
//   //                   },
//   //                   ':disabled': {
//   //                     opacity: 0.4,                            // Disable opacity effect
//   //                     cursor: 'not-allowed',                   // Disable cursor effect
//   //                   }
//   //                 }}>
//   //                   Finalize
//   //                 </Button>
//   //               )}
//   //               {finalized && <Badge color="success">✓ Finalized</Badge>}
//   //             </div>

//   //             {/* Tabs */}
//   //             <div style={{ borderBottom: '1px solid var(--border-subtle)', marginBottom: 16, display: 'flex' }}>
//   //               <TabBtn id="document"   label="Document" />
//   //               <TabBtn id="compliance" label="Compliance" />
//   //               <TabBtn id="feedback"   label="Feedback" count={feedbackLog.length} />
//   //               <TabBtn id="placeholders" label="Placeholders" count={generationResult.sections?.filter(s => s.has_placeholders)?.length || 0} />
//   //               <TabBtn id="sources"    label="Sources" />
//   //             </div>

//   //             {/* Tab content */}
//   //             <AnimatePresence mode="wait">
//   //               <motion.div key={activeTab}
//   //                 initial={{ opacity: 0, y: 6 }} animate={{ opacity: 1, y: 0 }}
//   //                 transition={{ duration: 0.2 }}>

//   //                 {activeTab === 'document' && (
//   //                   <DocumentViewer result={generationResult} />
//   //                 )}

//   //                 {activeTab === 'compliance' && (
//   //                   <CompliancePanel report={generationResult.compliance_report} />
//   //                 )}

//   //                 {activeTab === 'feedback' && (
//   //                   <FeedbackMechanism
//   //                     sections={generationResult.sections || []}
//   //                     sessionId={sessionId}
//   //                   />
//   //                 )}

//   //                 {activeTab === 'placeholders' && (
//   //                 <Card>
//   //                   <div style={{ fontSize: 13, fontWeight: 500, marginBottom: 4,
//   //                     display: 'flex', alignItems: 'center', gap: 8 }}>
//   //                     <Tag size={14} color="var(--accent)" />
//   //                     Fill Document Placeholders
//   //                   </div>
//   //                   <p style={{ fontSize: 12, color: 'var(--text-muted)', marginBottom: 16 }}>
//   //                     The AI may have left bracketed tokens like{' '}
//   //                     <code style={{ background: 'var(--bg-overlay)', padding: '1px 5px',
//   //                       borderRadius: 3, fontSize: 11, color: 'var(--warning)' }}>
//   //                       [INVESTIGATIONAL_PRODUCT]
//   //                     </code>{' '}
//   //                     where it did not have specific values. Fill them in below to complete the document.
//   //                   </p>
//   //                   <PlaceholderManager
//   //                     sessionId={sessionId}
//   //                     sections={generationResult.sections?.filter(s => s.has_placeholders)}
//   //                     onFilled={handlePlaceholdersFilled}
//   //                   />
//   //                 </Card>
//   //               )}

//   //                 {activeTab === 'sources' && (
//   //                   <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(240px, 1fr))', gap: 10 }}>
//   //                     {(generationResult.retrieved_sources || []).map((src, i) => (
//   //                       <Card key={i} hover>
//   //                         <div style={{ fontSize: 20, marginBottom: 8 }}>📄</div>
//   //                         <div style={{ fontSize: 13, fontWeight: 500, marginBottom: 4, color: 'var(--text-primary)' }}>{src}</div>
//   //                         <div style={{ fontSize: 11, color: 'var(--text-muted)' }}>
//   //                           Retrieved from vector store · Score: {(0.72 + Math.random() * 0.25).toFixed(3)}
//   //                         </div>
//   //                       </Card>
//   //                     ))}
//   //                     <Card hover >
//   //                       <div style={{ fontSize: 20, marginBottom: 8 }}>⚖️</div>
//   //                       <div style={{ fontSize: 13, fontWeight: 500, color: 'var(--text-primary)', marginBottom: 4 }}>Regulatory Guidelines</div>
//   //                       <div style={{ fontSize: 11, color: 'var(--text-muted)' }}>ICH E6(R2) · ICH E8 · FDA 21 CFR · EMA Guidelines</div>
//   //                     </Card>
//   //                   </div>
//   //                 )}
//   //               </motion.div>
//   //             </AnimatePresence>
//   //           </motion.div>
//   //         )}
//   //       </AnimatePresence>
//   //     </div>
//   //   </div>
//   // )
//   return (
//     <div style={{ display: 'flex', flexDirection: 'column', height: '100vh', overflow: 'hidden' }}>
//       <Topbar
//         title="Clinical Trial Document Generator"
//         subtitle="RAG-Powered · Groq LLM · ICH E6/E3 Compliant"
//       />
 
//       <div style={{ flex: 1, overflow: 'auto', padding: '20px 24px' }}>
//         <AnimatePresence mode="wait">
 
//           {/* ── Step 0: Form ─────────────────────────────────────────────── */}
//           {currentStep === 0 && (
//             <motion.div key="form"
//               initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -8 }}
//               transition={{ duration: 0.3 }}
//               style={{ maxWidth: 720, margin: '0 auto' }}>
 
//               <div style={{ marginBottom: 24, textAlign: 'center' }}>
//                 <h1 style={{ fontFamily: 'var(--font-display)', fontSize: 28, marginBottom: 6, color: 'var(--text-primary)' }}>
//                   Generate Clinical Trial Documents
//                 </h1>
//                 <p style={{ fontSize: 14, color: 'var(--text-muted)', maxWidth: 480, margin: '0 auto' }}>
//                   AI-powered drafting with FAISS retrieval, Groq LLM generation, and automated compliance validation.
//                 </p>
//                 {serverStatus !== 'online' && (
//                   <div style={{ marginTop: 10, display: 'inline-flex', alignItems: 'center', gap: 6, fontSize: 12, color: 'var(--warning)', background: 'var(--warning-dim)', padding: '4px 12px', borderRadius: 20, border: '1px solid rgba(245,166,35,0.3)' }}>
//                     ⚠ API offline — using mock generation
//                   </div>
//                 )}
//               </div>
 
//               <StudyMetadataForm onSubmit={handleGenerate} isLoading={isGenerating} />
//             </motion.div>
//           )}
 
//           {/* ── Step 1: Progress ─────────────────────────────────────────── */}
//           {currentStep === 1 && (
//             <motion.div key="progress"
//               initial={{ opacity: 0, scale: 0.97 }} animate={{ opacity: 1, scale: 1 }} exit={{ opacity: 0 }}
//               transition={{ duration: 0.3 }}
//               style={{ maxWidth: 560, margin: '0 auto' }}>
//               <GenerationProgress />
//             </motion.div>
//           )}
 
//           {/* ── Step 2: Document preview + Review button ─────────────────── */}
//           {currentStep >= 2 && generationResult && (
//             <motion.div key="preview"
//               initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }}
//               transition={{ duration: 0.35 }}>
 
//               {/* Stats row */}
//               <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 10, marginBottom: 16 }}>
//                 <StatCard
//                   label="Sections" icon={<FileText size={14} />}
//                   value={generationResult.sections?.length || 0}
//                   color="var(--info)"
//                 />
//                 <StatCard
//                   label="Total Words" icon={<Database size={14} />}
//                   value={(generationResult.total_words || generationResult.sections?.reduce((s, sec) => s + (sec.word_count || 0), 0) || 0).toLocaleString()}
//                   color="var(--accent)"
//                 />
//                 <StatCard
//                   label="Compliance" icon={<CheckCircle size={14} />}
//                   value={`${Math.round(generationResult.compliance_report?.overall_score || 0)}%`}
//                   color={generationResult.compliance_report?.is_compliant ? 'var(--success)' : 'var(--danger)'}
//                 />
//                 <StatCard
//                   label="RAG Sources" icon={<Zap size={14} />}
//                   value={generationResult.retrieved_sources?.length || 0}
//                   color="var(--info)"
//                 />
//               </div>
 
//               {/* Header row: label + Review button */}
//               <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 16 }}>
//                 <div>
//                   <span style={{ fontSize: 13, fontWeight: 500, color: 'var(--text-primary)' }}>
//                     {documentType}
//                   </span>
//                   <span style={{ fontSize: 12, color: 'var(--text-muted)', marginLeft: 8 }}>
//                     · {sessionId?.slice(-8)}
//                   </span>
//                 </div>
 
//                 <Button
//                   variant="primary"
//                   size="sm"
//                   icon={<ChevronRight size={14} />}
//                   onClick={() => navigate('/review')}
//                   style={{
//                     display: 'inline-flex', alignItems: 'center', gap: 6,
//                     padding: '8px 18px', borderRadius: '0.5rem',
//                     fontSize: '0.875rem', fontWeight: 500,
//                     background: 'var(--accent)', color: 'var(--bg-base)',
//                     border: 'none', cursor: 'pointer',
//                     boxShadow: '0 2px 8px var(--accent-glow)',
//                     transition: 'all 0.2s ease',
//                   }}
//                 >
//                   Review Document
//                 </Button>
//               </div>
 
//               {/* Document preview (read-only, no tabs) */}
//               <DocumentViewer result={generationResult} />
 
//             </motion.div>
//           )}
 
//         </AnimatePresence>
//       </div>
//     </div>
//   )
// }

// // ── Mock data when API offline ─────────────────────────────────────────────────
// function buildMockResult(formData) {
//   const meta = formData.metadata
//   const sections = [
//     {
//       section_id: 'intro', title: '1. Introduction and Rationale',
//       content: `This ${meta.phase} study evaluates ${meta.investigational_product || '[Drug]'} in patients with ${meta.patient_population}. The study is conducted in accordance with [INVESTIGATIONAL_PRODUCT] ICH E6(R2) Good Clinical Practice guidelines.\n\n**Disease Background:** ${meta.indication} remains a significant clinical challenge with substantial unmet medical need. Current therapies provide limited durable benefit, highlighting the need for novel therapeutic approaches.\n\n**Study Rationale:** Based on preclinical and early clinical data, ${meta.investigational_product || 'the investigational product'} demonstrates a compelling mechanistic rationale for this patient population. This study is designed to confirm clinical benefit and establish a robust benefit-risk profile consistent with regulatory requirements.`,
//       word_count: 102, confidence_score: 0.87, sources_used: ['Historical Trial CSP 2022', 'ICH E8 Guidelines'], revised: false,
//     },
//     {
//       section_id: 'study_design', title: '2. Study Design',
//       content: `This is a ${meta.design} study. Patients will be randomized ${meta.treatment_arms?.length > 1 ? `${meta.treatment_arms.length}:1` : '1:1'} to receive ${meta.treatment_arms?.join(' or ') || 'investigational product or placebo'}.\n\n**Randomization:** Patients will be randomized using an Interactive Web Response System (IWRS). Randomization will be stratified by geographic region, prior treatment history, and disease characteristics.\n\n**Sample Size:** ${meta.sample_size || 'TBD'} patients enrolled across approximately 150 sites globally over ${meta.duration_months || 'TBD'} months.`,
//       word_count: 95, confidence_score: 0.84, sources_used: ['Historical Trial CSP 2022'], revised: false,
//     },
//     {
//       section_id: 'objectives', title: '3. Study Objectives and Endpoints',
//       content: `**Primary Objective:** To evaluate the efficacy of ${meta.investigational_product || '[Drug]'} as measured by ${meta.primary_endpoint}.\n\n**Primary Endpoint:** ${meta.primary_endpoint} — defined as time from randomization to event, assessed per standard criteria.\n\n**Secondary Endpoints:**\n${(meta.secondary_endpoints || ['PFS', 'ORR']).map((ep, i) => `${i + 1}. ${ep}`).join('\n')}\n\nAll endpoints are pre-specified per ICH E9(R1) estimand framework.`,
//       word_count: 88, confidence_score: 0.91, sources_used: ['ICH E9 Guidelines'], revised: false,
//     },
//     {
//       section_id: 'population', title: '4. Study Population',
//       content: `**Inclusion Criteria:**\n1. Adults ≥18 years with confirmed ${meta.indication}\n2. ${meta.patient_population}\n3. ECOG Performance Status 0-1 at screening\n4. Measurable disease per applicable disease criteria\n5. Adequate organ function (haematology, hepatic, renal)\n6. Life expectancy ≥3 months\n7. Willing to provide written informed consent\n\n**Exclusion Criteria:**\n1. Prior treatment with drugs of the same class\n2. Active or untreated CNS metastases\n3. Active autoimmune disease requiring systemic treatment\n4. Pregnancy or breastfeeding\n5. Known active infection requiring systemic therapy`,
//       word_count: 110, confidence_score: 0.88, sources_used: ['Historical Trial CSP 2022', 'ICH E6 Guidelines'], revised: false,
//     },
//     {
//       section_id: 'statistics', title: '5. Statistical Methodology',
//       content: `**Primary Analysis:** The primary endpoint will be analysed using a stratified log-rank test (two-sided alpha=0.05). Hazard ratios and 95% confidence intervals will be estimated using a stratified Cox proportional hazards model.\n\n**Sample Size:** ${meta.sample_size || 'N'} patients provide 80% statistical power to detect a hazard ratio of 0.73, assuming median ${meta.primary_endpoint} of 18 months (control) and 24.7 months (treatment).\n\n**Analysis Populations:** Intent-to-Treat (ITT) population is the primary analysis set. Per-Protocol (PP) and Safety populations provide supportive analyses.\n\n**Missing Data:** Multiple imputation under Missing At Random (MAR) assumption per ICH E9(R1).`,
//       word_count: 115, confidence_score: 0.85, sources_used: ['ICH E9(R1) Guidelines', 'Historical SAP'], revised: false,
//     },
//   ]

//   const compliance = {
//     overall_score: 82,
//     is_compliant: true,
//     issues: [
//       { severity: 'warning', category: 'regulatory', description: '[CSP-006] Explicit GCP reference recommended', suggestion: 'Add reference to ICH E6(R2) GCP', regulatory_ref: 'ICH E6', rule_id: 'CSP-006' },
//       { severity: 'info', category: 'formatting', description: 'Statistical section may benefit from additional detail', suggestion: 'Specify interim analysis alpha-spending function', regulatory_ref: 'ICH E9', rule_id: 'SAP-004' },
//     ],
//     guidelines_checked: ['ICH E6(R2)', 'ICH E8', 'ICH E9(R1)', 'FDA 21 CFR 312', 'GCP'],
//     entities_validated: {
//       'Adverse Events': ['adverse event', 'SAE', 'CTCAE'],
//       'Endpoints': [meta.primary_endpoint, ...(meta.secondary_endpoints || []).slice(0, 2)],
//       'Regulatory': ['ICH E6', 'ICH E9', 'GCP', 'IRB'],
//       'Statistical': ['ITT', 'hazard ratio', 'confidence interval'],
//     },
//     missing_sections: [],
//     recommendations: [
//       'Have document reviewed by a qualified medical writer',
//       `Verify primary endpoint pre-specification for ${meta.phase} confirmatory trial`,
//       'Schedule pre-submission meeting with regulatory authority for Phase III',
//     ],
//   }

//   return {
//     session_id: `MOCK-${Date.now().toString(36).toUpperCase()}`,
//     document_type: formData.document_type,
//     sections,
//     compliance_report: compliance,
//     retrieved_sources: ['Phase III Breast Cancer Protocol 2022.pdf', 'ICH E6 GCP Guidelines.pdf', 'FDA Statistical Guidance.pdf'],
//     metadata: meta,
//     status: 'generated',
//     generated_at: new Date().toISOString(),
//     total_words: sections.reduce((s, sec) => s + sec.word_count, 0),
//     model_used: 'mock',
//   }
// }
import { useState, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import toast from 'react-hot-toast'
import { Zap, FileText, CheckCircle, ChevronRight, Database } from 'lucide-react'
import { useAppStore } from '../store/appStore'
import { apiService } from '../services/api.js'
import StudyMetadataForm from '../components/forms/StudyMetadataForm.jsx'
import GenerationProgress from '../components/document/GenerationProgress.jsx'
import DocumentViewer from '../components/document/DocumentViewer.jsx'
import Topbar from '../components/layout/Topbar.jsx'
import { Button, Badge, StatCard } from '../components/ui/index.jsx'

const PIPELINE_STAGES = [0, 1, 2, 3, 4]
const STAGE_DURATIONS = [800, 600, 400, 700, 500]

function mockPipeline(setStage) {
  return new Promise((resolve) => {
    let s = 0
    const next = () => {
      setStage(s)
      s++
      if (s < PIPELINE_STAGES.length) setTimeout(next, STAGE_DURATIONS[s] || 600)
      else setTimeout(resolve, 400)
    }
    next()
  })
}

function buildMockResult(formData) {
  const meta = formData.metadata
  const sections = [
    {
      section_id: 'intro', title: '1. Introduction and Rationale',
      content: `This ${meta.phase} study evaluates ${meta.investigational_product || '[Drug]'} in patients with ${meta.patient_population}. The study is conducted in accordance with ICH E6(R2) Good Clinical Practice guidelines.\n\n**Disease Background:** ${meta.indication} remains a significant clinical challenge. Current therapies provide limited durable benefit, highlighting the need for novel therapeutic approaches.\n\n**Study Rationale:** Based on preclinical and early clinical data, ${meta.investigational_product || 'the investigational product'} demonstrates a compelling mechanistic rationale for this patient population.`,
      word_count: 102, confidence_score: 0.87, sources_used: ['Historical Trial CSP 2022', 'ICH E8 Guidelines'], revised: false,
    },
    {
      section_id: 'study_design', title: '2. Study Design',
      content: `This is a ${meta.design} study. Patients will be randomized ${meta.treatment_arms?.length > 1 ? `${meta.treatment_arms.length}:1` : '1:1'} to receive ${meta.treatment_arms?.join(' or ') || 'investigational product or placebo'}.\n\n**Randomization:** Patients will be randomized using an Interactive Web Response System (IWRS), stratified by geographic region, prior treatment history, and disease characteristics.\n\n**Sample Size:** ${meta.sample_size || 'TBD'} patients enrolled across approximately 150 sites globally over ${meta.duration_months || 'TBD'} months.`,
      word_count: 95, confidence_score: 0.84, sources_used: ['Historical Trial CSP 2022'], revised: false,
    },
    {
      section_id: 'objectives', title: '3. Study Objectives and Endpoints',
      content: `**Primary Objective:** To evaluate the efficacy of ${meta.investigational_product || '[Drug]'} as measured by ${meta.primary_endpoint}.\n\n**Primary Endpoint:** ${meta.primary_endpoint} — defined as time from randomization to event, assessed per standard criteria.\n\n**Secondary Endpoints:**\n${(meta.secondary_endpoints || ['PFS', 'ORR']).map((ep, i) => `${i + 1}. ${ep}`).join('\n')}\n\nAll endpoints are pre-specified per ICH E9(R1) estimand framework.`,
      word_count: 88, confidence_score: 0.91, sources_used: ['ICH E9 Guidelines'], revised: false,
    },
    {
      section_id: 'population', title: '4. Study Population',
      content: `**Inclusion Criteria:**\n1. Adults ≥18 years with confirmed ${meta.indication}\n2. ${meta.patient_population}\n3. ECOG Performance Status 0-1 at screening\n4. Measurable disease per applicable disease criteria\n5. Adequate organ function\n\n**Exclusion Criteria:**\n1. Prior treatment with drugs of the same class\n2. Active or untreated CNS metastases\n3. Active autoimmune disease requiring systemic treatment\n4. Pregnancy or breastfeeding`,
      word_count: 110, confidence_score: 0.88, sources_used: ['Historical Trial CSP 2022', 'ICH E6 Guidelines'], revised: false,
    },
    {
      section_id: 'statistics', title: '5. Statistical Methodology',
      content: `**Primary Analysis:** The primary endpoint will be analysed using a stratified log-rank test (two-sided alpha=0.05). Hazard ratios and 95% CIs will be estimated using a stratified Cox proportional hazards model.\n\n**Sample Size:** ${meta.sample_size || 'N'} patients provide 80% power to detect a hazard ratio of 0.73.\n\n**Analysis Populations:** Intent-to-Treat (ITT) is the primary analysis set. Per-Protocol (PP) and Safety populations provide supportive analyses.`,
      word_count: 115, confidence_score: 0.85, sources_used: ['ICH E9(R1) Guidelines', 'Historical SAP'], revised: false,
    },
  ]
  return {
    session_id: `MOCK-${Date.now().toString(36).toUpperCase()}`,
    document_type: formData.document_type,
    sections,
    compliance_report: {
      overall_score: 82, is_compliant: true,
      issues: [
        { severity: 'warning', category: 'regulatory', description: '[CSP-006] Explicit GCP reference recommended', suggestion: 'Add reference to ICH E6(R2) GCP', regulatory_ref: 'ICH E6', rule_id: 'CSP-006' },
      ],
      guidelines_checked: ['ICH E6(R2)', 'ICH E8', 'ICH E9(R1)', 'FDA 21 CFR 312'],
      missing_sections: [],
      recommendations: ['Have document reviewed by a qualified medical writer'],
    },
    retrieved_sources: ['Phase III Breast Cancer Protocol 2022.pdf', 'ICH E6 GCP Guidelines.pdf'],
    metadata: meta,
    status: 'generated',
    total_words: sections.reduce((s, sec) => s + sec.word_count, 0),
  }
}

export default function GeneratePage() {
  const navigate = useNavigate()
  const {
    currentStep, setStep,
    generationStage, setGenerationStage,
    generationResult, setGenerationResult,
    sessionId, setSessionId,
    isGenerating, setIsGenerating,
    documentType, setDocumentType,
    setSections,
    serverStatus, setComplianceReport,
  } = useAppStore()

  const handleGenerate = useCallback(async (formData) => {
    setIsGenerating(true)
    setStep(1)
    setGenerationStage(-1)
    setDocumentType(formData.document_type)

    const pipelineP = mockPipeline(setGenerationStage)

    try {
      let result
      if (serverStatus === 'online') {
        const [apiResult] = await Promise.all([
          apiService.generateDocument({
            metadata:                 formData.metadata,
            document_type:            formData.document_type,
            rag_top_k:                formData.rag_top_k,
            include_compliance_check: true,
            additional_context:       formData.additional_context,
            model_tier:               formData.model_tier,
          }),
          pipelineP,
        ])
        result = apiResult
      } else {
        await pipelineP
        await new Promise(r => setTimeout(r, 600))
        result = buildMockResult(formData)
      }

      setSessionId(result.session_id)
      setGenerationResult(result)
      setSections(result.sections || [])
      setComplianceReport(result.compliance_report || {})
      setStep(2)
      toast.success(`${formData.document_type} generated!`)
    } catch (err) {
      toast.error(err.message || 'Generation failed')
      setStep(0)
    } finally {
      setIsGenerating(false)
      setGenerationStage(-1)
    }
  }, [serverStatus])

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100vh', overflow: 'hidden' }}>
      <Topbar
        title="Clinical Trial Document Generator"
        subtitle="RAG-Powered · Groq LLM · ICH E6/E3 Compliant"
      />

      <div style={{ flex: 1, overflow: 'auto', padding: '20px 24px' }}>
        <AnimatePresence mode="wait">

          {/* ── Step 0: Form ─────────────────────────────────────────────── */}
          {currentStep === 0 && (
            <motion.div key="form"
              initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -8 }}
              transition={{ duration: 0.3 }}
              style={{ maxWidth: 720, margin: '0 auto' }}>

              <div style={{ marginBottom: 24, textAlign: 'center' }}>
                <h1 style={{ fontFamily: 'var(--font-display)', fontSize: 28, marginBottom: 6, color: 'var(--text-primary)' }}>
                  Generate Clinical Trial Documents
                </h1>
                <p style={{ fontSize: 14, color: 'var(--text-muted)', maxWidth: 480, margin: '0 auto' }}>
                  AI-powered drafting with FAISS retrieval, Groq LLM generation, and automated compliance validation.
                </p>
                {serverStatus !== 'online' && (
                  <div style={{ marginTop: 10, display: 'inline-flex', alignItems: 'center', gap: 6, fontSize: 12, color: 'var(--warning)', background: 'var(--warning-dim)', padding: '4px 12px', borderRadius: 20, border: '1px solid rgba(245,166,35,0.3)' }}>
                    ⚠ API offline — using mock generation
                  </div>
                )}
              </div>

              <StudyMetadataForm onSubmit={handleGenerate} isLoading={isGenerating} />
            </motion.div>
          )}

          {/* ── Step 1: Progress ─────────────────────────────────────────── */}
          {currentStep === 1 && (
            <motion.div key="progress"
              initial={{ opacity: 0, scale: 0.97 }} animate={{ opacity: 1, scale: 1 }} exit={{ opacity: 0 }}
              transition={{ duration: 0.3 }}
              style={{ maxWidth: 560, margin: '0 auto' }}>
              <GenerationProgress />
            </motion.div>
          )}

          {/* ── Step 2: Document preview + Review button ─────────────────── */}
          {currentStep >= 2 && generationResult && (
            <motion.div key="preview"
              initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.35 }}>

              {/* Stats row */}
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 10, marginBottom: 16 }}>
                <StatCard
                  label="Sections" icon={<FileText size={14} />}
                  value={generationResult.sections?.length || 0}
                  color="var(--info)"
                />
                <StatCard
                  label="Total Words" icon={<Database size={14} />}
                  value={(generationResult.total_words || generationResult.sections?.reduce((s, sec) => s + (sec.word_count || 0), 0) || 0).toLocaleString()}
                  color="var(--accent)"
                />
                <StatCard
                  label="Compliance" icon={<CheckCircle size={14} />}
                  value={`${Math.round(generationResult.compliance_report?.overall_score || 0)}%`}
                  color={generationResult.compliance_report?.is_compliant ? 'var(--success)' : 'var(--danger)'}
                />
                <StatCard
                  label="RAG Sources" icon={<Zap size={14} />}
                  value={generationResult.retrieved_sources?.length || 0}
                  color="var(--info)"
                />
              </div>

              {/* Header row: label + Review button */}
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 16 }}>
                <div>
                  <span style={{ fontSize: 13, fontWeight: 500, color: 'var(--text-primary)' }}>
                    {documentType}
                  </span>
                  <span style={{ fontSize: 12, color: 'var(--text-muted)', marginLeft: 8 }}>
                    · {sessionId?.slice(-8)}
                  </span>
                </div>

                <Button
                  variant="primary"
                  size="sm"
                  icon={<ChevronRight size={14} />}
                  onClick={() => navigate('/review')}
                  style={{
                    display: 'inline-flex', alignItems: 'center', gap: 6,
                    padding: '8px 18px', borderRadius: '0.5rem',
                    fontSize: '0.875rem', fontWeight: 500,
                    background: 'var(--accent)', color: 'var(--bg-base)',
                    border: 'none', cursor: 'pointer',
                    boxShadow: '0 2px 8px var(--accent-glow)',
                    transition: 'all 0.2s ease',
                  }}
                >
                  Review Document
                </Button>
              </div>

              {/* Document preview (read-only, no tabs) */}
              <DocumentViewer result={generationResult} />

            </motion.div>
          )}

        </AnimatePresence>
      </div>
    </div>
  )
}
