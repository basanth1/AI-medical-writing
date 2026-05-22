import { useForm } from 'react-hook-form'
import { Save, User, Server, Sliders, Shield, Moon, Sun } from 'lucide-react'
import toast from 'react-hot-toast'
import { useAppStore } from '../store/appStore.js'
import { Button, Input, Select, Card } from '../components/ui/index.jsx'
import { REVIEWER_ROLES, MODEL_TIERS, RAG_TOP_K_OPTIONS, COMPLIANCE_GUIDELINES } from '../data/constants.js'
import { THEMES } from '../data/theme.js'
import Topbar from '../components/layout/Topbar.jsx'

export default function SettingsPage() {
  const { userPrefs, setUserPrefs, serverStatus, theme, toggleTheme } = useAppStore()
  const { register, handleSubmit } = useForm({ defaultValues: userPrefs })

  const onSave = (data) => { setUserPrefs(data); toast.success('Preferences saved') }

  const Section = ({ title, icon: Icon, children }) => (
    <Card style={{ marginBottom: 16 }}>
      <div style={{ display:'flex', alignItems:'center', gap:8, marginBottom:16 }}>
        <Icon size={15} color="var(--accent)" />
        <h2 style={{ fontSize:14, fontWeight:500 }}>{title}</h2>
      </div>
      {children}
    </Card>
  )

  return (
    <div style={{ display:'flex', flexDirection:'column', height:'100vh', overflow:'hidden' }}>
      <Topbar title="Settings" subtitle="Configure your preferences and API connections" />
      <div style={{ flex:1, overflow:'auto', padding:'20px 24px' }}>
        <form onSubmit={handleSubmit(onSave)} style={{ maxWidth:600, margin:'0 auto' }}>

          {/* Appearance */}
          <Section title="Appearance" icon={theme.name === 'dark' ? Moon : Sun}>
            <div style={{ display:'flex', alignItems:'center', justifyContent:'space-between', padding:'12px 0' }}>
              <div>
                <div style={{ fontSize:13, fontWeight:500, color:'var(--text-primary)' }}>
                  {theme.name === 'dark' ? 'Dark Mode' : 'Light Mode'}
                </div>
                <div style={{ fontSize:12, color:'var(--text-muted)', marginTop:2 }}>
                  {theme.name === 'dark' ? 'Using dark theme — easier on the eyes' : 'Using light theme — high contrast'}
                </div>
              </div>
              <div style={{ display:'flex', gap:8 }}>
                {Object.values(THEMES).map(t => (
                  <button key={t.name} type="button" onClick={() => { if (t.name !== theme.name) toggleTheme() }}
                    style={{
                      padding:'8px 16px', borderRadius:'var(--radius-md)', cursor:'pointer',
                      border:`1.5px solid ${theme.name === t.name ? 'var(--accent)' : 'var(--border-soft)'}`,
                      background: theme.name === t.name ? 'var(--accent-glow)' : 'var(--bg-elevated)',
                      color: theme.name === t.name ? 'var(--accent-text)' : 'var(--text-secondary)',
                      fontSize:12, fontWeight: theme.name === t.name ? 500 : 400,
                      display:'flex', alignItems:'center', gap:6, transition:'all 0.15s',
                    }}>
                    {t.name === 'dark' ? <Moon size={13} /> : <Sun size={13} />}
                    {t.label}
                  </button>
                ))}
              </div>
            </div>
          </Section>

          {/* User Profile */}
          <Section title="User Profile" icon={User}>
            <div style={{ display:'grid', gridTemplateColumns:'1fr 1fr', gap:10 }}>
              <Input label="Full Name" {...register('name')} placeholder="Dr. Jane Smith" />
              <Select label="Default Role" {...register('role')}>
                {REVIEWER_ROLES.map(r => <option key={r}>{r}</option>)}
              </Select>
              <div style={{ gridColumn:'span 2' }}>
                <Input label="Organization" {...register('organization')} placeholder="PharmaCo Inc." />
              </div>
            </div>
          </Section>

          {/* API */}
          <Section title="API Configuration" icon={Server}>
            <div style={{ padding:'10px 14px', borderRadius:'var(--radius-md)',
              background:'var(--bg-elevated)', border:'1px solid var(--border-subtle)', marginBottom:10 }}>
              <div style={{ display:'flex', alignItems:'center', gap:8, marginBottom:4 }}>
                <div style={{ width:8, height:8, borderRadius:'50%',
                  background: serverStatus==='online' ? 'var(--success)' : 'var(--danger)',
                  boxShadow: serverStatus==='online' ? '0 0 6px var(--success)' : 'none' }} />
                <span style={{ fontSize:13, fontWeight:500 }}>
                  {serverStatus==='online' ? 'Backend API Online' : 'Backend API Offline'}
                </span>
              </div>
              <span style={{ fontSize:11, color:'var(--text-muted)' }}>
                {serverStatus==='online'
                  ? 'Connected — Ollama gpt-oss:120b (primary) · Groq llama-3.3-70b (fallback)'
                  : 'Set OLLAMA_API_KEY + GROQ_API_KEY, then run: python app.py'}
              </span>
            </div>
            <Input label="API Base URL" defaultValue={import.meta.env.VITE_API_BASE || 'http://127.0.0.1:8765/api/v1'}
              hint="Configure with VITE_API_BASE env var" readOnly />
          </Section>

          {/* Generation */}
          <Section title="Generation Preferences" icon={Sliders}>
            <div style={{ display:'grid', gridTemplateColumns:'1fr 1fr', gap:10 }}>
              <Select label="Default Model Tier" {...register('defaultModel')}>
                {MODEL_TIERS.map(m => <option key={m.value} value={m.value}>{m.label}</option>)}
              </Select>
              <Select label="Default RAG Top-K" {...register('defaultTopK')}>
                {RAG_TOP_K_OPTIONS.map(n => <option key={n} value={n}>{n} documents</option>)}
              </Select>
            </div>
            <div style={{ display:'flex', gap:16, marginTop:10 }}>
              <label style={{ display:'flex', alignItems:'center', gap:8, cursor:'pointer', fontSize:13, color:'var(--text-secondary)' }}>
                <input type="checkbox" {...register('autoCompliance')} defaultChecked style={{ accentColor:'var(--accent)' }} />
                Auto-run compliance after generation
              </label>
              <label style={{ display:'flex', alignItems:'center', gap:8, cursor:'pointer', fontSize:13, color:'var(--text-secondary)' }}>
                <input type="checkbox" {...register('compactView')} style={{ accentColor:'var(--accent)' }} />
                Compact section view
              </label>
            </div>
          </Section>

          {/* Compliance */}
          <Section title="Compliance Standards" icon={Shield}>
            <div style={{ fontSize:12, color:'var(--text-muted)', marginBottom:10 }}>
              Active regulatory standards (always enforced):
            </div>
            <div style={{ display:'flex', flexWrap:'wrap', gap:6 }}>
              {[...new Set(Object.values(COMPLIANCE_GUIDELINES).flat())].map(s => (
                <span key={s} style={{ fontSize:11, padding:'3px 9px', borderRadius:10,
                  background:'var(--accent-glow)', color:'var(--accent-text)', border:'1px solid var(--accent-dim)' }}>
                  {s}
                </span>
              ))}
            </div>
          </Section>

          <Button type="submit" size="lg" style={{ width:'100%' }} icon={<Save size={15} />}>
            Save Preferences
          </Button>
        </form>
      </div>
    </div>
  )
}
