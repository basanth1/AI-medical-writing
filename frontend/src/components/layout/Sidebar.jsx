import { useState } from 'react'
import { NavLink, useLocation } from 'react-router-dom'
import {
  FileText, Settings, BarChart3, MessageSquare,
  Upload, ChevronLeft, ChevronRight, Dna,
  ShieldCheck, LogOut,
} from 'lucide-react'
import { useAppStore } from '../../store/appStore.js'
import { Badge } from '../ui/index.jsx'
import { NAV_ITEMS } from '../../data/constants.js'
import { API_ORIGIN } from '../../services/api.js'
import BrandLogo from '../brand/BrandLogo.jsx'

// Icon map — keyed by string from NAV_ITEMS
const ICON_MAP = { Dna, FileText, MessageSquare, Upload, ShieldCheck, BarChart3, Settings }

export default function Sidebar() {
  const [collapsed, setCollapsed] = useState(false)
  const { serverStatus, feedbackLog, ollamaAvailable, groqAvailable } = useAppStore()
  const location = useLocation()

  return (
    <aside style={{
      width: collapsed ? 70 : 220, minHeight: '100vh',
      background: 'var(--bg-surface)', borderRight: '1px solid var(--border-subtle)',
      display: 'flex', flexDirection: 'column',
      transition: 'width 0.25s cubic-bezier(0.4,0,0.2,1)',
      flexShrink: 0, zIndex: 10,
    }}>
      {/* Logo */}
      <div style={{
        padding: collapsed ? '28px 0' : '18px 16px',
        borderBottom: '1px solid var(--border-subtle)',
        display: 'flex', alignItems: 'center',
        justifyContent: collapsed ? 'center' : 'space-between', gap: 8,
      }}>
        <BrandLogo markSize={32} compact={collapsed} />
        <button onClick={() => setCollapsed(!collapsed)} style={{
          background: 'none', border: 'none', cursor: 'pointer',
          color: 'var(--text-muted)', padding: 2, borderRadius: 4,
          display: 'flex', alignItems: 'center', flexShrink: 0,
        }}>
          {collapsed ? <ChevronRight size={14} /> : <ChevronLeft size={14} />}
        </button>
      </div>

      {/* Nav */}
      <nav style={{ flex: 1, padding: '10px 8px', display: 'flex', flexDirection: 'column', gap: 2 }}>
        {NAV_ITEMS.map(({ to, iconKey, label, end }) => {
          const Icon = ICON_MAP[iconKey] || FileText
          const isActive = end ? location.pathname === to : location.pathname.startsWith(to)
          const showBadge = to === '/feedback' && feedbackLog.length > 0

          return (
            <NavLink key={to} to={to} style={{
              display: 'flex', alignItems: 'center', gap: 10,
              padding: collapsed ? '9px 0' : '9px 10px',
              justifyContent: collapsed ? 'center' : 'flex-start',
              borderRadius: 'var(--radius-md)', textDecoration: 'none',
              color: isActive ? 'var(--accent-text)' : 'var(--text-secondary)',
              background: isActive ? 'var(--accent-glow)' : 'transparent',
              border: `1px solid ${isActive ? 'var(--accent-dim)' : 'transparent'}`,
              transition: 'all 0.15s', fontSize: 13,
              fontWeight: isActive ? 500 : 400, position: 'relative',
            }}
              onMouseEnter={e => { if (!isActive) e.currentTarget.style.background = 'var(--bg-hover)' }}
              onMouseLeave={e => { if (!isActive) e.currentTarget.style.background = 'transparent' }}>
              <Icon size={16} style={{ flexShrink: 0 }} />
              {!collapsed && (
                <>
                  <span style={{ whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>{label}</span>
                  {showBadge && (
                    <Badge color="accent" size="xs" style={{ marginLeft: 'auto' }}>{feedbackLog.length}</Badge>
                  )}
                </>
              )}
            </NavLink>
          )
        })}
      </nav>

      {/* Server + LLM status */}
      <div style={{
        padding: collapsed ? '10px 0' : '10px 12px',
        borderTop: '1px solid var(--border-subtle)',
      }}>
        {/* API dot + label */}
        <div style={{
          display: 'flex', alignItems: 'center',
          justifyContent: collapsed ? 'center' : 'flex-start', gap: 7, marginBottom: collapsed ? 0 : 5,
        }}>
          <div style={{
            width: 7, height: 7, borderRadius: '50%', flexShrink: 0,
            background: serverStatus === 'online' ? 'var(--success)'
                      : serverStatus === 'offline' ? 'var(--danger)' : 'var(--text-muted)',
            boxShadow: serverStatus === 'online' ? '0 0 6px var(--success)' : 'none',
            animation: serverStatus === 'checking' ? 'pulse 1.2s infinite' : 'none',
          }} />
          {!collapsed && (
            <span style={{ fontSize: 11, color: 'var(--text-muted)' }}>
              {serverStatus === 'online' ? 'API Online' : serverStatus === 'offline' ? 'API Offline' : 'Connecting…'}
            </span>
          )}
        </div>
        {/* Ollama + Groq indicators */}
        {!collapsed && serverStatus === 'online' && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 3, paddingLeft: 14 }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 5 }}>
              <div style={{
                width: 5, height: 5, borderRadius: '50%', flexShrink: 0,
                background: ollamaAvailable ? 'var(--success)' : 'var(--border-mid)',
              }} />
              <span style={{ fontSize: 10, color: ollamaAvailable ? 'var(--success)' : 'var(--text-muted)' }}>
                Ollama {ollamaAvailable ? 'gpt-oss:120b' : 'offline'}
              </span>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: 5 }}>
              <div style={{
                width: 5, height: 5, borderRadius: '50%', flexShrink: 0,
                background: groqAvailable ? 'var(--info)' : 'var(--border-mid)',
              }} />
              <span style={{ fontSize: 10, color: groqAvailable ? 'var(--info)' : 'var(--text-muted)' }}>
                Groq {groqAvailable ? 'llama-3.3-70b ↩' : 'offline'}
              </span>
            </div>
          </div>
        )}
      </div>

      {/* Sign Out */}
      <div style={{
        padding: collapsed ? '10px 0' : '10px 12px',
        borderTop: '1px solid var(--border-subtle)',
      }}>
        <button
          onClick={() => {
            const form = document.createElement('form')
            form.method = 'POST'
            form.action = `${API_ORIGIN}/auth/logout`
            document.body.appendChild(form)
            form.submit()
          }}
          style={{
            display: 'flex', alignItems: 'center', gap: 10,
            padding: collapsed ? '9px 0' : '9px 10px',
            justifyContent: collapsed ? 'center' : 'flex-start',
            borderRadius: 'var(--radius-md)', border: 'none', cursor: 'pointer',
            background: 'transparent', color: 'var(--danger)',
            width: '100%', fontSize: 13, fontWeight: 500, transition: 'all 0.15s'
          }}
          onMouseEnter={e => e.currentTarget.style.background = 'rgba(255, 92, 92, 0.1)'}
          onMouseLeave={e => e.currentTarget.style.background = 'transparent'}
        >
          <LogOut size={16} style={{ flexShrink: 0 }} />
          {!collapsed && <span>Sign Out</span>}
        </button>
      </div>
    </aside>
  )
}
