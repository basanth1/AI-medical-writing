import { useState, useCallback } from 'react'
import { Upload, File, CheckCircle, X, Database, Plus } from 'lucide-react'
import { motion } from 'framer-motion'
import Topbar from '../components/layout/Topbar.jsx'
import { Button, Card, Input, Select, Badge } from '../components/ui/index.jsx'
import { INGEST_DOC_TYPES } from '../data/constants.js'
import { apiService } from '../services/api.js'
import { useAppStore } from '../store/appStore.js'
import toast from 'react-hot-toast'

export default function IngestPage() {
  const { serverStatus, vectorStats, setVectorStats } = useAppStore()
  const [files, setFiles]               = useState([])
  const [dragging, setDragging]         = useState(false)
  const [uploading, setUploading]       = useState(false)
  const [ingestedDocs, setIngestedDocs] = useState([])
  const [docType, setDocType]           = useState('historical_trial')
  const [manualText, setManualText]     = useState('')
  const [manualType, setManualType]     = useState('historical_trial')
  const [manualIndication, setManualIndication] = useState('')
  const [ingestingText, setIngestingText] = useState(false)
  const [tab, setTab]                   = useState('file')

  const onDrop = useCallback((e) => {
    e.preventDefault(); setDragging(false)
    const dropped = Array.from(e.dataTransfer?.files || e.target?.files || [])
    const valid   = dropped.filter(f => f.name.match(/\.(pdf|txt|json|docx)$/i))
    if (valid.length !== dropped.length) toast.error('Only PDF, TXT, JSON, DOCX supported')
    setFiles(prev => [...prev, ...valid.map(f => ({ file:f, status:'pending', id:Math.random().toString(36).slice(2) }))])
  }, [])

  const uploadAll = async () => {
    if (!files.length) return toast.error('No files selected')
    setUploading(true)
    for (const item of files) {
      if (item.status === 'done') continue
      setFiles(prev => prev.map(f => f.id === item.id ? { ...f, status:'uploading' } : f))
      try {
        const result = serverStatus === 'online'
          ? await apiService.ingestDocument(item.file, docType)
          : await new Promise(r => setTimeout(() => r({ doc_id: Math.random().toString(36).slice(2,10), chunks_created: Math.floor(Math.random()*12)+3 }), 800))
        setFiles(prev => prev.map(f => f.id === item.id ? { ...f, status:'done', result } : f))
        setIngestedDocs(prev => [...prev, { name: item.file.name, ...result, type: docType }])
        toast.success(`Ingested: ${item.file.name}`)
      } catch (err) {
        setFiles(prev => prev.map(f => f.id === item.id ? { ...f, status:'error', error:err.message } : f))
        toast.error(`Failed: ${item.file.name}`)
      }
    }
    setUploading(false)
  }

  const ingestText = async () => {
    if (!manualText.trim()) return toast.error('Enter text to ingest')
    setIngestingText(true)
    try {
      const result = serverStatus === 'online'
        ? await apiService.ingestMetadata({ text: manualText, doc_type: manualType, indication: manualIndication })
        : await new Promise(r => setTimeout(() => r({ doc_id: Math.random().toString(36).slice(2,10), chunks_created: Math.ceil(manualText.split(' ').length/500) }), 600))
      setIngestedDocs(prev => [...prev, { name: 'Manual Text Entry', ...result, type: manualType }])
      setManualText('')
      toast.success(`Text ingested (${result.chunks_created} chunks)`)
    } catch (err) {
      toast.error(err.message)
    } finally {
      setIngestingText(false)
    }
  }

  const statusEl = (status) => ({
    pending:   <span style={{ color:'var(--text-muted)', fontSize:11 }}>pending</span>,
    uploading: <span style={{ color:'var(--info)', fontSize:11, animation:'pulse 1s infinite' }}>uploading…</span>,
    done:      <CheckCircle size={14} color="var(--success)" />,
    error:     <X size={14} color="var(--danger)" />,
  }[status])

  const TabBtn = ({ id, label }) => (
    <button onClick={() => setTab(id)} style={{
      padding:'7px 16px', border:'none',
      borderBottom:`2px solid ${tab===id ? 'var(--accent)' : 'transparent'}`,
      background:'transparent', fontSize:13,
      fontWeight: tab===id ? 500 : 400,
      color: tab===id ? 'var(--accent-text)' : 'var(--text-muted)',
      cursor:'pointer', transition:'all 0.15s',
    }}>{label}</button>
  )

  return (
    <div style={{ display:'flex', flexDirection:'column', height:'100vh', overflow:'hidden' }}>
      <Topbar title="Data Ingestion" subtitle="Add documents to the FAISS vector knowledge base" />
      <div style={{ flex:1, overflow:'auto', padding:'20px 24px' }}>
        <div style={{ display:'grid', gridTemplateColumns:'1fr 280px', gap:16, maxWidth:1000, margin:'0 auto' }}>
          <div>
            <div style={{ display:'flex', borderBottom:'1px solid var(--border-subtle)', marginBottom:16 }}>
              <TabBtn id="file" label="Upload Files" />
              <TabBtn id="text" label="Paste Text" />
            </div>

            {tab === 'file' && (
              <div style={{ display:'flex', flexDirection:'column', gap:12 }}>
                <Select label="Document Type" value={docType} onChange={e => setDocType(e.target.value)} >
                  {INGEST_DOC_TYPES.map(t => <option key={t} value={t}>{t.replace(/_/g,' ')}</option>)}
                </Select>
                <div
                  onDragOver={e => { e.preventDefault(); setDragging(true) }}
                  onDragLeave={() => setDragging(false)}
                  onDrop={onDrop}
                  onClick={() => document.getElementById('file-input').click()}
                  style={{
                    border:`2px dashed ${dragging ? 'var(--accent)' : 'var(--border-soft)'}`,
                    borderRadius:'var(--radius-lg)', padding:'32px 24px', textAlign:'center',
                    background: dragging ? 'var(--accent-glow)' : 'var(--bg-elevated)',
                    cursor:'pointer', transition:'all 0.15s', marginBottom:14,
                  }}>
                  <input id="file-input" type="file" multiple accept=".pdf,.txt,.json,.docx" onChange={onDrop} style={{ display:'none' }} />
                  <Upload size={28} color={dragging ? 'var(--accent)' : 'var(--text-muted)'} style={{ marginBottom:10 }} />
                  <p style={{ fontSize:13, color: dragging ? 'var(--accent-text)' : 'var(--text-secondary)', marginBottom:4 }}>
                    {dragging ? 'Drop files here' : 'Drag & drop or click to browse'}
                  </p>
                  <p style={{ fontSize:11, color:'var(--text-muted)' }}>PDF, TXT, JSON, DOCX supported</p>
                </div>
                {files.length > 0 && (
                  <div style={{ marginBottom:12 }}>
                    {files.map(item => (
                      <div key={item.id} style={{ display:'flex', alignItems:'center', gap:10, padding:'8px 12px',
                        background:'var(--bg-elevated)', borderRadius:'var(--radius-md)', marginBottom:6,
                        border:'1px solid var(--border-subtle)' }}>
                        <File size={14} color="var(--accent)" />
                        <span style={{ flex:1, fontSize:12, color:'var(--text-secondary)', overflow:'hidden', textOverflow:'ellipsis', whiteSpace:'nowrap' }}>{item.file.name}</span>
                        <span style={{ fontSize:11, color:'var(--text-muted)' }}>{(item.file.size/1024).toFixed(0)}KB</span>
                        {statusEl(item.status)}
                        <button onClick={() => setFiles(f => f.filter(x => x.id !== item.id))}
                          style={{ background:'none', border:'none', cursor:'pointer', color:'var(--text-muted)', padding:2 }}>
                          <X size={12} />
                        </button>
                      </div>
                    ))}
                    <Button loading={uploading} onClick={uploadAll} style={{ width:'100%', marginTop:6 }} icon={<Database size={14} />}>
                      Ingest {files.filter(f => f.status !== 'done').length} File(s) into Vector Store
                    </Button>
                  </div>
                )}
              </div>
            )}

            {tab === 'text' && (
              <div>
                <div style={{ display:'grid', gridTemplateColumns:'1fr 1fr', gap:10, marginBottom:10 }}>
                  <Select label="Document Type" value={manualType} onChange={e => setManualType(e.target.value)}>
                    {INGEST_DOC_TYPES.map(t => <option key={t} value={t}>{t.replace(/_/g,' ')}</option>)}
                  </Select>
                  <Input label="Indication" value={manualIndication} onChange={e => setManualIndication(e.target.value)} placeholder="e.g. Oncology" />
                </div>
                <div style={{ marginBottom:4 }}>
                  <label style={{ fontSize:12, fontWeight:500, color:'var(--text-secondary)', display:'block', marginBottom:4 }}>Document Text *</label>
                  <textarea value={manualText} onChange={e => setManualText(e.target.value)} rows={10}
                    placeholder="Paste clinical trial document text here…"
                    style={{ width:'100%', background:'var(--bg-elevated)', border:'1px solid var(--border-soft)',
                      borderRadius:'var(--radius-md)', padding:'10px 12px', fontSize:12, color:'var(--text-primary)',
                      fontFamily:'var(--font-body)', lineHeight:1.6, resize:'vertical', outline:'none',
                      transition:'border-color 0.15s' }}
                    onFocus={e => e.target.style.borderColor = 'var(--accent)'}
                    onBlur={e  => e.target.style.borderColor = 'var(--border-soft)'} />
                  <div style={{ fontSize:11, color:'var(--text-muted)', marginTop:3 }}>
                    ~{Math.ceil(manualText.split(' ').filter(Boolean).length/500)} chunk(s) will be created
                  </div>
                </div>
                <Button loading={ingestingText} onClick={ingestText} style={{ width:'100%' }} icon={<Plus size={14} />}>
                  Ingest Text
                </Button>
              </div>
            )}
          </div>

          <div style={{ display:'flex', flexDirection:'column', gap:12 }}>
            <Card>
              <h3 style={{ fontSize:13, fontWeight:500, marginBottom:12 }}>Vector Store</h3>
              {vectorStats ? (
                <div style={{ display:'flex', flexDirection:'column', gap:8 }}>
                  {[['Type', vectorStats.retriever_type], ['Documents', vectorStats.total_documents],
                    ['Chunks', vectorStats.total_chunks], ['Vectors', vectorStats.index_size]].map(([k,v]) => (
                    <div key={k} style={{ display:'flex', justifyContent:'space-between', fontSize:12 }}>
                      <span style={{ color:'var(--text-muted)' }}>{k}</span>
                      <span style={{ fontWeight:500, color:'var(--text-primary)' }}>{v}</span>
                    </div>
                  ))}
                </div>
              ) : (
                <p style={{ fontSize:12, color:'var(--text-muted)' }}>Connect to backend to see stats.</p>
              )}
            </Card>

            <Card>
              <h3 style={{ fontSize:13, fontWeight:500, marginBottom:10 }}>
                Ingested This Session
                {ingestedDocs.length > 0 && <Badge color="accent" size="xs" style={{ marginLeft:6 }}>{ingestedDocs.length}</Badge>}
              </h3>
              {ingestedDocs.length === 0
                ? <p style={{ fontSize:12, color:'var(--text-muted)' }}>No documents ingested yet.</p>
                : ingestedDocs.map((doc,i) => (
                  <div key={i} style={{ padding:'8px 0', borderBottom: i < ingestedDocs.length-1 ? '1px solid var(--border-subtle)' : 'none' }}>
                    <div style={{ fontSize:12, color:'var(--text-primary)', fontWeight:500, overflow:'hidden', textOverflow:'ellipsis', whiteSpace:'nowrap' }}>{doc.name}</div>
                    <div style={{ fontSize:10, color:'var(--text-muted)', marginTop:2 }}>ID: {doc.doc_id} · {doc.chunks_created} chunks</div>
                  </div>
                ))}
            </Card>
          </div>
        </div>
      </div>
    </div>
  )
}
