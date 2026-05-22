import { useEffect, useState } from 'react'
import { Card, ProgressBar, Spinner } from '../ui/index.jsx'
import { useAppStore } from '../../store/appStore.js'
import { PIPELINE_STAGES } from '../../data/constants.js'
import { CheckCircle2, Brain } from 'lucide-react'

export default function GenerationProgress() {
  const { generationStage, documentType } = useAppStore()
  const [elapsed, setElapsed] = useState(0)

  useEffect(() => {
    const t = setInterval(() => setElapsed(s => s + 1), 1000)
    return () => clearInterval(t)
  }, [])

  const progress = generationStage < 0 ? 5
    : Math.round(((generationStage + 1) / PIPELINE_STAGES.length) * 100)

  return (
    <div style={{ display:'flex', flexDirection:'column', alignItems:'center', gap:24, padding:'2rem 0' }}>
      <div style={{ position:'relative' }}>
        <div style={{ width:80, height:80, borderRadius:'50%',
          border:'2px solid var(--border-subtle)', display:'flex', alignItems:'center', justifyContent:'center' }}>
          <div style={{ width:60, height:60, borderRadius:'50%',
            border:'2px solid var(--border-soft)', borderTopColor:'var(--accent)',
            animation:'spin 1.2s linear infinite' }} />
          <Brain size={20} color="var(--accent)" style={{ position:'absolute' }} />
        </div>
      </div>

      <div style={{ textAlign:'center' }}>
        <h2 style={{ fontFamily:'var(--font-display)', fontSize:20, marginBottom:4 }}>
          Generating {documentType}
        </h2>
        <p style={{ fontSize:13, color:'var(--text-muted)' }}>
          {elapsed}s elapsed · AI-powered clinical document synthesis
        </p>
      </div>

      <div style={{ width:'100%', maxWidth:500 }}>
        <div style={{ display:'flex', justifyContent:'space-between', marginBottom:6 }}>
          <span style={{ fontSize:12, color:'var(--text-secondary)' }}>Pipeline progress</span>
          <span style={{ fontSize:12, fontWeight:500, color:'var(--accent)' }}>{progress}%</span>
        </div>
        <ProgressBar value={progress} color="var(--accent)" height={5} />
      </div>

      <Card style={{ width:'100%', maxWidth:500, padding:'6px 0' }}>
        {PIPELINE_STAGES.map((stage, i) => {
          const done   = i < generationStage
          const active = i === generationStage
          return (
            <div key={i} style={{
              display:'flex', alignItems:'center', gap:14, padding:'10px 16px',
              borderBottom: i < PIPELINE_STAGES.length - 1 ? '1px solid var(--border-subtle)' : 'none',
              opacity: i > generationStage ? 0.4 : 1, transition:'opacity 0.3s',
            }}>
              <div style={{
                width:28, height:28, borderRadius:'50%', flexShrink:0,
                display:'flex', alignItems:'center', justifyContent:'center',
                background: done ? 'var(--success-dim)' : active ? 'var(--accent-glow)' : 'var(--bg-overlay)',
                border: `1px solid ${done ? 'rgba(52,201,123,0.4)' : active ? 'var(--accent-dim)' : 'var(--border-subtle)'}`,
                transition:'all 0.3s',
              }}>
                {done   ? <CheckCircle2 size={14} color="var(--success)" />
                : active ? <Spinner size={14} color="var(--accent)" />
                :           <Brain size={12} color="var(--text-muted)" />}
              </div>
              <div style={{ flex:1 }}>
                <div style={{ fontSize:13,
                  fontWeight: active ? 500 : 400,
                  color: done ? 'var(--text-secondary)' : active ? 'var(--text-primary)' : 'var(--text-muted)',
                }}>
                  {stage.label}
                </div>
                {active && (
                  <div style={{ fontSize:11, color:'var(--text-muted)', marginTop:1, animation:'pulse 1.5s infinite' }}>
                    {stage.detail}
                  </div>
                )}
              </div>
              {done && <span style={{ fontSize:10, color:'var(--success)', fontWeight:600 }}>DONE</span>}
            </div>
          )
        })}
      </Card>
    </div>
  )
}
