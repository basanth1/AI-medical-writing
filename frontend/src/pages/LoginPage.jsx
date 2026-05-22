import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  CheckCircle2, Database, Lock, LogIn, ShieldCheck,
  UserRound, UserPlus, Mail, User, ArrowLeft, Eye, EyeOff,
} from 'lucide-react'
import toast from 'react-hot-toast'
import { apiService, API_ORIGIN } from '../services/api.js'
import { useAppStore } from '../store/appStore.js'
import ThemeToggle from '../components/ui/ThemeToggle.jsx'
import BrandLogo from '../components/brand/BrandLogo.jsx'
import { Badge } from '../components/ui/index.jsx'

export default function LoginPage() {
  const navigate = useNavigate()
  const { initTheme } = useAppStore()

  // Shared state
  const [mode, setMode] = useState('login') // 'login' | 'signup'
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  // Login fields
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [showPassword, setShowPassword] = useState(false)

  // Sign-up fields
  const [signupUsername, setSignupUsername] = useState('')
  const [signupPassword, setSignupPassword] = useState('')
  const [showSignupPassword, setShowSignupPassword] = useState(false)
  const [signupConfirm, setSignupConfirm] = useState('')
  const [showSignupConfirm, setShowSignupConfirm] = useState(false)
  const [signupFullName, setSignupFullName] = useState('')
  const [signupEmail, setSignupEmail] = useState('')

  useEffect(() => {
    initTheme()
    apiService.checkAuth()
      .then((session) => {
        if (session.role === 'admin') {
          window.location.assign(`${API_ORIGIN}/admin/ui`)
        } else {
          navigate('/', { replace: true })
        }
      })
      .catch(() => {})
  }, [initTheme, navigate])

  const switchMode = (next) => {
    setMode(next)
    setError('')
  }

  /* ── Login handler ────────────────────────────── */
  const handleLogin = async (event) => {
    event.preventDefault()
    setError('')
    setLoading(true)
    try {
      const session = await apiService.login({ username, password })
      toast.success(`Signed in as ${session.role}`)
      if (session.role === 'admin') {
        window.location.assign(`${API_ORIGIN}/admin/ui`)
      } else {
        navigate('/', { replace: true })
      }
    } catch (err) {
      setError(err.message || 'Invalid username or password')
    } finally {
      setLoading(false)
    }
  }

  /* ── Sign-up handler ──────────────────────────── */
  const handleSignup = async (event) => {
    event.preventDefault()
    setError('')

    if (signupPassword !== signupConfirm) {
      setError('Passwords do not match')
      return
    }
    if (signupPassword.length < 6) {
      setError('Password must be at least 6 characters')
      return
    }
    if (signupUsername.length < 3) {
      setError('Username must be at least 3 characters')
      return
    }

    setLoading(true)
    try {
      const result = await apiService.signup({
        username: signupUsername,
        password: signupPassword,
        full_name: signupFullName,
        email: signupEmail,
      })
      toast.success('Account created! Redirecting to login…')
      setTimeout(() => {
        switchMode('login')
      }, 500)
    } catch (err) {
      setError(err.message || 'Registration failed')
    } finally {
      setLoading(false)
    }
  }

  /* ── Shared styles ────────────────────────────── */
  const inputIconStyle = {
    position: 'absolute',
    left: 12,
    top: '50%',
    transform: 'translateY(-50%)',
    color: 'var(--text-muted)',
    pointerEvents: 'none',
  }

  const railItemStyle = {
    display: 'flex',
    alignItems: 'center',
    gap: 10,
    padding: '11px 12px',
    border: '1px solid var(--border-subtle)',
    borderRadius: 'var(--radius-md)',
    background: 'var(--bg-elevated)',
    color: 'var(--text-secondary)',
    fontSize: 13,
  }

  const linkBtnStyle = {
    background: 'none',
    border: 'none',
    color: 'var(--accent)',
    fontWeight: 600,
    fontSize: 13,
    cursor: 'pointer',
    padding: 0,
    textDecoration: 'underline',
    fontFamily: 'inherit',
  }

  /* ── Render login form ────────────────────────── */
  const renderLoginForm = () => (
    <form onSubmit={handleLogin} style={{
      width: '100%',
      maxWidth: 390,
      display: 'flex',
      flexDirection: 'column',
      gap: 16,
      margin: 'auto 0',
    }}>
      <div style={{ marginBottom: 6 }}>
        <Badge color="accent" icon={<ShieldCheck size={12} />}>Secure workspace</Badge>
        <h1 style={{ fontSize: 28, lineHeight: 1.2, marginTop: 18, marginBottom: 8, letterSpacing: 0 }}>
          Sign in to TrialDoc
        </h1>
        <p style={{ fontSize: 13, maxWidth: 340 }}>
          Access document generation, compliance review, and admin configuration from one controlled workspace.
        </p>
      </div>

      <label style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
        <span style={{ fontSize: 12, fontWeight: 600, color: 'var(--text-secondary)' }}>Username</span>
        <span style={{ position: 'relative', display: 'block' }}>
          <UserRound size={16} style={inputIconStyle} />
          <input
            value={username}
            onChange={(event) => setUsername(event.target.value)}
            autoComplete="username"
            placeholder="Enter your username"
            required
            style={{ paddingLeft: 38, height: 42, background: 'var(--bg-base)' }}
          />
        </span>
      </label>

      <label style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
        <span style={{ fontSize: 12, fontWeight: 600, color: 'var(--text-secondary)' }}>Password</span>
        <span style={{ position: 'relative', display: 'block' }}>
          <Lock size={16} style={inputIconStyle} />
          <input
            value={password}
            onChange={(event) => setPassword(event.target.value)}
            autoComplete="current-password"
            placeholder="Enter password"
            required
            type={showPassword ? 'text' : 'password'}
            style={{ paddingLeft: 38, paddingRight: 42, height: 42, background: 'var(--bg-base)' }}
          />
          <button
            type="button"
            onClick={() => setShowPassword(!showPassword)}
            style={{
              position: 'absolute',
              right: 12,
              top: '50%',
              transform: 'translateY(-50%)',
              background: 'none',
              border: 'none',
              color: 'var(--text-muted)',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              padding: 0,
            }}
          >
            {showPassword ? <EyeOff size={16} /> : <Eye size={16} />}
          </button>
        </span>
      </label>

      {error && (
        <div role="alert" style={{
          padding: '10px 12px',
          borderRadius: 'var(--radius-md)',
          border: '1px solid var(--danger)',
          background: 'var(--danger-dim)',
          color: 'var(--danger)',
          fontSize: 12,
        }}>
          {error}
        </div>
      )}

      <button
        type="submit"
        disabled={loading}
        style={{
          height: 42,
          border: '1px solid var(--accent)',
          borderRadius: 'var(--radius-md)',
          background: 'var(--accent)',
          color: 'var(--text-inverse)',
          fontWeight: 700,
          display: 'inline-flex',
          alignItems: 'center',
          justifyContent: 'center',
          gap: 8,
          opacity: loading ? 0.72 : 1,
          transition: 'opacity 0.15s, transform 0.15s',
        }}
      >
        <LogIn size={16} />
        {loading ? 'Signing in...' : 'Sign in'}
      </button>

      <div style={{
        display: 'flex', alignItems: 'center', gap: 12,
        margin: '4px 0', color: 'var(--text-muted)', fontSize: 12,
      }}>
        <span style={{ flex: 1, height: 1, background: 'var(--border-subtle)' }} />
        <span>or</span>
        <span style={{ flex: 1, height: 1, background: 'var(--border-subtle)' }} />
      </div>

      <button
        type="button"
        onClick={() => switchMode('signup')}
        style={{
          height: 42,
          border: '1px solid var(--border-subtle)',
          borderRadius: 'var(--radius-md)',
          background: 'var(--bg-elevated)',
          color: 'var(--text-secondary)',
          fontWeight: 600,
          display: 'inline-flex',
          alignItems: 'center',
          justifyContent: 'center',
          gap: 8,
          cursor: 'pointer',
          fontFamily: 'inherit',
          fontSize: 14,
          transition: 'border-color 0.15s, background 0.15s',
        }}
      >
        <UserPlus size={16} />
        Create an account
      </button>
    </form>
  )

  /* ── Render sign-up form ──────────────────────── */
  const renderSignupForm = () => (
    <form onSubmit={handleSignup} style={{
      width: '100%',
      maxWidth: 390,
      display: 'flex',
      flexDirection: 'column',
      gap: 14,
      margin: 'auto 0',
    }}>
      <div style={{ marginBottom: 2 }}>
        <button
          type="button"
          onClick={() => switchMode('login')}
          style={{
            ...linkBtnStyle,
            display: 'inline-flex', alignItems: 'center', gap: 4,
            textDecoration: 'none', marginBottom: 12, fontSize: 12,
            color: 'var(--text-muted)',
          }}
        >
          <ArrowLeft size={14} /> Back to sign in
        </button>
        <Badge color="success" icon={<UserPlus size={12} />}>New account</Badge>
        <h1 style={{ fontSize: 26, lineHeight: 1.2, marginTop: 14, marginBottom: 6, letterSpacing: 0 }}>
          Create your account
        </h1>
        <p style={{ fontSize: 13, maxWidth: 340, color: 'var(--text-secondary)' }}>
          Register to access document generation and compliance review.
          Admin access is provisioned by the team separately.
        </p>
      </div>

      {/* Full name */}
      <label style={{ display: 'flex', flexDirection: 'column', gap: 5 }}>
        <span style={{ fontSize: 12, fontWeight: 600, color: 'var(--text-secondary)' }}>Full Name</span>
        <span style={{ position: 'relative', display: 'block' }}>
          <User size={16} style={inputIconStyle} />
          <input
            value={signupFullName}
            onChange={(e) => setSignupFullName(e.target.value)}
            placeholder="John Doe"
            autoComplete="name"
            style={{ paddingLeft: 38, height: 42, background: 'var(--bg-base)' }}
          />
        </span>
      </label>

      {/* Email */}
      <label style={{ display: 'flex', flexDirection: 'column', gap: 5 }}>
        <span style={{ fontSize: 12, fontWeight: 600, color: 'var(--text-secondary)' }}>Email</span>
        <span style={{ position: 'relative', display: 'block' }}>
          <Mail size={16} style={inputIconStyle} />
          <input
            value={signupEmail}
            onChange={(e) => setSignupEmail(e.target.value)}
            placeholder="john@example.com"
            type="email"
            autoComplete="email"
            style={{ paddingLeft: 38, height: 42, background: 'var(--bg-base)' }}
          />
        </span>
      </label>

      {/* Username */}
      <label style={{ display: 'flex', flexDirection: 'column', gap: 5 }}>
        <span style={{ fontSize: 12, fontWeight: 600, color: 'var(--text-secondary)' }}>
          Username <span style={{ color: 'var(--danger)' }}>*</span>
        </span>
        <span style={{ position: 'relative', display: 'block' }}>
          <UserRound size={16} style={inputIconStyle} />
          <input
            value={signupUsername}
            onChange={(e) => setSignupUsername(e.target.value)}
            placeholder="Choose a username (min 3 chars)"
            autoComplete="username"
            required
            style={{ paddingLeft: 38, height: 42, background: 'var(--bg-base)' }}
          />
        </span>
      </label>

      {/* Password */}
      <label style={{ display: 'flex', flexDirection: 'column', gap: 5 }}>
        <span style={{ fontSize: 12, fontWeight: 600, color: 'var(--text-secondary)' }}>
          Password <span style={{ color: 'var(--danger)' }}>*</span>
        </span>
        <span style={{ position: 'relative', display: 'block' }}>
          <Lock size={16} style={inputIconStyle} />
          <input
            value={signupPassword}
            onChange={(e) => setSignupPassword(e.target.value)}
            placeholder="Min 6 characters"
            type={showSignupPassword ? 'text' : 'password'}
            autoComplete="new-password"
            required
            style={{ paddingLeft: 38, paddingRight: 42, height: 42, background: 'var(--bg-base)' }}
          />
          <button
            type="button"
            onClick={() => setShowSignupPassword(!showSignupPassword)}
            style={{
              position: 'absolute',
              right: 12,
              top: '50%',
              transform: 'translateY(-50%)',
              background: 'none',
              border: 'none',
              color: 'var(--text-muted)',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              padding: 0,
            }}
          >
            {showSignupPassword ? <EyeOff size={16} /> : <Eye size={16} />}
          </button>
        </span>
      </label>

      {/* Confirm password */}
      <label style={{ display: 'flex', flexDirection: 'column', gap: 5 }}>
        <span style={{ fontSize: 12, fontWeight: 600, color: 'var(--text-secondary)' }}>
          Confirm Password <span style={{ color: 'var(--danger)' }}>*</span>
        </span>
        <span style={{ position: 'relative', display: 'block' }}>
          <Lock size={16} style={inputIconStyle} />
          <input
            value={signupConfirm}
            onChange={(e) => setSignupConfirm(e.target.value)}
            placeholder="Re-enter password"
            type={showSignupConfirm ? 'text' : 'password'}
            autoComplete="new-password"
            required
            style={{ paddingLeft: 38, paddingRight: 42, height: 42, background: 'var(--bg-base)' }}
          />
          <button
            type="button"
            onClick={() => setShowSignupConfirm(!showSignupConfirm)}
            style={{
              position: 'absolute',
              right: 12,
              top: '50%',
              transform: 'translateY(-50%)',
              background: 'none',
              border: 'none',
              color: 'var(--text-muted)',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              padding: 0,
            }}
          >
            {showSignupConfirm ? <EyeOff size={16} /> : <Eye size={16} />}
          </button>
        </span>
      </label>

      {error && (
        <div role="alert" style={{
          padding: '10px 12px',
          borderRadius: 'var(--radius-md)',
          border: '1px solid var(--danger)',
          background: 'var(--danger-dim)',
          color: 'var(--danger)',
          fontSize: 12,
        }}>
          {error}
        </div>
      )}

      <button
        type="submit"
        disabled={loading}
        style={{
          height: 42,
          border: 'none',
          borderRadius: 'var(--radius-md)',
          background: 'linear-gradient(135deg, var(--accent), var(--success))',
          color: '#fff',
          fontWeight: 700,
          display: 'inline-flex',
          alignItems: 'center',
          justifyContent: 'center',
          gap: 8,
          fontSize: 14,
          fontFamily: 'inherit',
          cursor: loading ? 'not-allowed' : 'pointer',
          opacity: loading ? 0.72 : 1,
          transition: 'opacity 0.15s, transform 0.15s',
          boxShadow: '0 4px 16px rgba(0,196,140,0.18)',
        }}
      >
        <UserPlus size={16} />
        {loading ? 'Creating account...' : 'Create account'}
      </button>

      <p style={{ textAlign: 'center', fontSize: 12, color: 'var(--text-muted)', marginTop: 2 }}>
        Already have an account?{' '}
        <button type="button" onClick={() => switchMode('login')} style={linkBtnStyle}>
          Sign in
        </button>
      </p>
    </form>
  )

  /* ── Sidebar rail content ─────────────────────── */
  const renderRail = () => (
    <aside className="login-context-rail" style={{
      borderLeft: '1px solid var(--border-soft)',
      background: 'var(--bg-base)',
      padding: 24,
      display: 'flex',
      flexDirection: 'column',
      justifyContent: 'space-between',
      gap: 24,
    }}>
      <div>
        <div style={{
          fontSize: 11,
          fontWeight: 700,
          color: 'var(--text-muted)',
          textTransform: 'uppercase',
          letterSpacing: '.08em',
          marginBottom: 12,
        }}>
          {mode === 'login' ? 'Workspace Access' : 'What You Get'}
        </div>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
          {mode === 'login' ? (
            <>
              <div style={railItemStyle}>
                <ShieldCheck size={16} color="var(--accent)" />
                Admin configuration
              </div>
              <div style={railItemStyle}>
                <Database size={16} color="var(--success)" />
                Document generation
              </div>
              <div style={railItemStyle}>
                <CheckCircle2 size={16} color="var(--warning)" />
                Compliance review
              </div>
            </>
          ) : (
            <>
              <div style={railItemStyle}>
                <Database size={16} color="var(--success)" />
                Full document generation
              </div>
              <div style={railItemStyle}>
                <CheckCircle2 size={16} color="var(--warning)" />
                Compliance review tools
              </div>
              <div style={railItemStyle}>
                <UserRound size={16} color="var(--accent)" />
                Personal workspace
              </div>
              <div style={{
                ...railItemStyle,
                background: 'rgba(124,58,237,0.06)',
                border: '1px solid rgba(124,58,237,0.15)',
                color: 'var(--text-secondary)',
                fontSize: 12,
                lineHeight: 1.5,
              }}>
                <ShieldCheck size={16} color="rgba(124,58,237,0.7)" />
                <span>Admin access is provisioned separately by your team lead</span>
              </div>
            </>
          )}
        </div>
      </div>

      <div style={{
        paddingTop: 16,
        borderTop: '1px solid var(--border-subtle)',
        color: 'var(--text-muted)',
        fontSize: 12,
        lineHeight: 1.6,
      }}>
        Authorized access for clinical and regulatory document workflows.
      </div>
    </aside>
  )

  /* ── Main render ──────────────────────────────── */
  return (
    <main className="login-page" style={{
      minHeight: '100vh',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      padding: 24,
      background: 'var(--bg-base)',
      color: 'var(--text-primary)',
    }}>
      <section className="login-shell" style={{
        width: '100%',
        maxWidth: 940,
        minHeight: 520,
        display: 'grid',
        gridTemplateColumns: 'minmax(0, 1fr) 300px',
        border: '1px solid var(--border-soft)',
        borderRadius: 'var(--radius-xl)',
        background: 'var(--bg-surface)',
        boxShadow: '0 24px 70px rgba(0,0,0,0.22)',
        overflow: 'hidden',
      }}>
        <div style={{
          display: 'flex',
          flexDirection: 'column',
          padding: 32,
          minWidth: 0,
        }}>
          <div style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            gap: 16,
            marginBottom: mode === 'login' ? 42 : 20,
            transition: 'margin 0.2s ease',
          }}>
            <BrandLogo markSize={42} title="TrialDoc" subtitle="AI Generator" />
            <ThemeToggle />
          </div>

          {mode === 'login' ? renderLoginForm() : renderSignupForm()}
        </div>

        {renderRail()}
      </section>
    </main>
  )
}
