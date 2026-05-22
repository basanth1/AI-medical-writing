"""
backend/api/login_ui_html.py
Self-contained login page served at /login.
Dark-themed, glassmorphism card, animated background.
"""
LOGIN_UI_HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
<title>Trial Doc — Sign In</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<style>
  *{box-sizing:border-box;margin:0;padding:0}
  :root{
    --bg:#070b14;--card:rgba(15,20,35,0.82);--border:rgba(255,255,255,0.06);
    --text:#f0f4ff;--text2:#8b9cc0;--muted:#4a5a7a;
    --accent:#20beff;--accent2:#7c3aed;--danger:#ff5c5c;--success:#00c48c;
    --input-bg:rgba(20,28,50,0.7);--input-border:rgba(40,55,85,0.8);
    --radius:14px;
    font-family:'Inter',system-ui,sans-serif;
    color-scheme:dark;
  }
  :root[data-theme="light"]{
    --bg:#ffffff;--card:rgba(248,250,252,0.9);--border:rgba(13,27,46,0.08);
    --text:#0d1b2e;--text2:#3a5068;--muted:#7a90a8;
    --accent:#0099d8;--accent2:#5166d6;--danger:#dc2626;--success:#00a572;
    --input-bg:rgba(241,245,249,0.86);--input-border:#d1dcf0;
    color-scheme:light;
  }
  html,body{height:100%;overflow:hidden}
  body{
    background:var(--bg);color:var(--text);
    display:flex;align-items:center;justify-content:center;
    position:relative;
  }
  /* ── Animated background ── */
  .bg-gradient{
    position:fixed;inset:0;z-index:0;
    background:
      radial-gradient(ellipse 80% 60% at 20% 80%, rgba(124,58,237,0.12) 0%, transparent 60%),
      radial-gradient(ellipse 70% 50% at 80% 20%, rgba(32,190,255,0.10) 0%, transparent 50%),
      radial-gradient(ellipse 50% 40% at 50% 50%, rgba(32,190,255,0.04) 0%, transparent 50%),
      linear-gradient(160deg, #070b14 0%, #0d1225 40%, #10162e 70%, #070b14 100%);
  }
  :root[data-theme="light"] .bg-gradient{
    background:
      radial-gradient(ellipse 80% 60% at 20% 80%, rgba(81,102,214,0.10) 0%, transparent 60%),
      radial-gradient(ellipse 70% 50% at 80% 20%, rgba(0,153,216,0.12) 0%, transparent 50%),
      radial-gradient(ellipse 50% 40% at 50% 50%, rgba(0,165,114,0.06) 0%, transparent 50%),
      linear-gradient(160deg, #ffffff 0%, #f8fafc 42%, #eef5fb 72%, #ffffff 100%);
  }
  .bg-grid{
    position:fixed;inset:0;z-index:0;
    background-image:
      linear-gradient(rgba(255,255,255,0.015) 1px, transparent 1px),
      linear-gradient(90deg, rgba(255,255,255,0.015) 1px, transparent 1px);
    background-size:60px 60px;
  }
  :root[data-theme="light"] .bg-grid{
    background-image:
      linear-gradient(rgba(13,27,46,0.04) 1px, transparent 1px),
      linear-gradient(90deg, rgba(13,27,46,0.04) 1px, transparent 1px);
  }
  .orb{
    position:fixed;border-radius:50%;filter:blur(80px);opacity:0.3;z-index:0;
    animation:float 12s ease-in-out infinite alternate;
  }
  .orb-1{width:300px;height:300px;background:rgba(32,190,255,0.15);top:10%;left:15%;animation-delay:-2s}
  .orb-2{width:250px;height:250px;background:rgba(124,58,237,0.12);bottom:15%;right:10%;animation-delay:-6s}
  .orb-3{width:200px;height:200px;background:rgba(0,196,140,0.08);top:60%;left:60%;animation-delay:-4s}
  :root[data-theme="light"] .orb{opacity:0.22}
  :root[data-theme="light"] .orb-1{background:rgba(0,153,216,0.18)}
  :root[data-theme="light"] .orb-2{background:rgba(81,102,214,0.14)}
  :root[data-theme="light"] .orb-3{background:rgba(0,165,114,0.12)}
  @keyframes float{
    0%{transform:translate(0,0) scale(1)}
    50%{transform:translate(20px,-30px) scale(1.08)}
    100%{transform:translate(-10px,15px) scale(0.95)}
  }
  /* ── Login card ── */
  .login-card{
    position:relative;z-index:1;
    width:440px;max-width:92vw;
    background:var(--card);
    border:1px solid var(--border);
    border-radius:20px;
    padding:48px 40px 40px;
    backdrop-filter:blur(24px);-webkit-backdrop-filter:blur(24px);
    box-shadow:0 30px 80px rgba(0,0,0,0.45),0 0 0 1px rgba(255,255,255,0.03) inset;
    animation:cardIn 0.5s ease-out;
  }
  :root[data-theme="light"] .login-card{
    box-shadow:0 30px 80px rgba(13,27,46,0.12),0 0 0 1px rgba(255,255,255,0.6) inset;
  }
  .theme-toggle{
    position:fixed;top:18px;right:18px;z-index:2;
    width:38px;height:38px;display:inline-flex;align-items:center;justify-content:center;
    background:var(--card);color:#ffb020;border:1px solid var(--border);
    border-radius:12px;cursor:pointer;font-size:17px;line-height:1;
    backdrop-filter:blur(18px);-webkit-backdrop-filter:blur(18px);
    box-shadow:0 12px 30px rgba(0,0,0,0.18);
    transition:transform 0.15s,border-color 0.15s,background 0.15s,color 0.15s;
  }
  .theme-toggle:hover{transform:scale(1.06);border-color:var(--accent)}
  :root[data-theme="light"] .theme-toggle{color:var(--accent);box-shadow:0 12px 30px rgba(13,27,46,0.10)}
  @keyframes cardIn{
    from{opacity:0;transform:translateY(24px) scale(0.97)}
    to{opacity:1;transform:none}
  }
  /* ── Logo ── */
  .logo{text-align:center;margin-bottom:36px}
  .logo-icon{
    width:56px;height:56px;border-radius:16px;
    background:linear-gradient(135deg,rgba(32,190,255,0.15),rgba(124,58,237,0.15));
    border:1px solid rgba(32,190,255,0.2);
    display:inline-flex;align-items:center;justify-content:center;
    font-size:26px;margin-bottom:14px;
    box-shadow:0 0 30px rgba(32,190,255,0.1);
  }
  .logo-text{font-size:22px;font-weight:800;letter-spacing:-0.03em;margin-bottom:4px}
  .logo-text span{background:linear-gradient(135deg,var(--accent),var(--accent2));-webkit-background-clip:text;-webkit-text-fill-color:transparent}
  .logo-sub{font-size:13px;color:var(--muted);font-weight:400}
  /* ── Form ── */
  .form-group{margin-bottom:18px;position:relative}
  .form-group label{display:block;font-size:12px;font-weight:500;color:var(--text2);margin-bottom:6px;letter-spacing:0.02em}
  .input-wrap{position:relative}
  .input-icon{
    position:absolute;left:14px;top:50%;transform:translateY(-50%);
    font-size:15px;color:var(--muted);pointer-events:none;transition:color 0.2s;
  }
  .form-input{
    width:100%;padding:13px 16px 13px 42px;
    background:var(--input-bg);
    border:1.5px solid var(--input-border);
    border-radius:var(--radius);
    color:var(--text);font-size:14px;font-family:inherit;
    outline:none;transition:border-color 0.2s,box-shadow 0.2s;
  }
  .form-input::placeholder{color:var(--muted);font-size:13px}
  .form-input:focus{
    border-color:var(--accent);
    box-shadow:0 0 0 3px rgba(32,190,255,0.1);
  }
  .form-input:focus + .input-icon-focus,
  .form-input:focus ~ .input-icon{color:var(--accent)}
  /* ── Password toggle ── */
  .pw-toggle{
    position:absolute;right:12px;top:50%;transform:translateY(-50%);
    background:none;border:none;color:var(--muted);cursor:pointer;
    font-size:15px;padding:4px;transition:color 0.15s;
  }
  .pw-toggle:hover{color:var(--text2)}
  /* ── Submit button ── */
  .submit-btn{
    width:100%;padding:14px;margin-top:8px;
    background:linear-gradient(135deg,var(--accent),var(--accent2));
    border:none;border-radius:var(--radius);
    color:#fff;font-size:14px;font-weight:600;font-family:inherit;
    cursor:pointer;position:relative;overflow:hidden;
    transition:transform 0.15s,box-shadow 0.15s;
    box-shadow:0 4px 20px rgba(32,190,255,0.2);
  }
  .submit-btn:hover{transform:translateY(-1px);box-shadow:0 6px 28px rgba(32,190,255,0.3)}
  .submit-btn:active{transform:translateY(0)}
  .submit-btn:disabled{opacity:0.6;cursor:not-allowed;transform:none}
  .submit-btn .spinner{
    display:inline-block;width:16px;height:16px;
    border:2px solid rgba(255,255,255,0.3);border-top-color:#fff;
    border-radius:50%;animation:spin 0.6s linear infinite;
    vertical-align:middle;margin-right:8px;
  }
  @keyframes spin{to{transform:rotate(360deg)}}
  /* ── Error ── */
  .error-msg{
    background:rgba(255,92,92,0.1);border:1px solid rgba(255,92,92,0.25);
    border-radius:10px;padding:10px 14px;margin-bottom:18px;
    font-size:13px;color:var(--danger);display:none;
    animation:shake 0.35s ease;
  }
  @keyframes shake{
    0%,100%{transform:translateX(0)}
    20%,60%{transform:translateX(-6px)}
    40%,80%{transform:translateX(6px)}
  }
  /* ── Divider ── */
  .divider{
    display:flex;align-items:center;gap:12px;margin:22px 0 18px;
    font-size:11px;color:var(--muted);text-transform:uppercase;letter-spacing:0.08em;
  }
  .divider::before,.divider::after{content:'';flex:1;height:1px;background:var(--input-border)}
  /* ── Role hint ── */
  .role-hints{
    display:grid;grid-template-columns:1fr 1fr;gap:8px;
  }
  .role-hint{
    background:rgba(173, 216, 230,0.8);border:1px solid var(--input-border);
    border-radius:10px;padding:10px 12px;cursor:pointer;
    transition:border-color 0.15s,background 0.15s;
  }
  .role-hint:hover{border-color:rgba(32,190,255,0.3);background:rgba(32,190,255,0.04)}
  .role-hint-title{font-size:12px;font-weight:600;margin-bottom:2px;display:flex;align-items:center;gap:5px}
  .role-hint-desc{font-size:10px;color:var(--muted);line-height:1.4}
  .role-hint .dot{width:6px;height:6px;border-radius:50%;display:inline-block}
  .dot-admin{background:var(--accent2)}
  .dot-user{background:var(--success)}
  /* ── Footer ── */
  .login-footer{
    text-align:center;margin-top:28px;
    font-size:11px;color:var(--muted);
  }
  .login-footer a{color:var(--accent);text-decoration:none}
  .login-footer a:hover{text-decoration:underline}
  /* ── Scrollbar ── */
  ::-webkit-scrollbar{width:4px}
  ::-webkit-scrollbar-track{background:transparent}
  ::-webkit-scrollbar-thumb{background:rgba(255,255,255,0.08);border-radius:99px}
</style>
</head>
<body>
<div class="bg-gradient"></div>
<div class="bg-grid"></div>
<div class="orb orb-1"></div>
<div class="orb orb-2"></div>
<div class="orb orb-3"></div>
<button class="theme-toggle" id="theme-toggle" type="button"
        onclick="toggleTheme()" title="Switch to light mode"
        aria-label="Switch to light mode">☀</button>
<div class="login-card" id="login-panel">
  <div class="logo">
    <div class="logo-icon">⚗</div>
    <div class="logo-text"><span>Trial Doc</span></div>
    <div class="logo-sub">Clinical Trial Document Generation System</div>
  </div>
  <div class="error-msg" id="error-msg"></div>
  <form id="login-form" autocomplete="off">
    <div class="form-group">
      <label for="username">Username</label>
      <div class="input-wrap">
        <input class="form-input" id="username" name="username" type="text"
               placeholder="Enter your username" autocomplete="username" required />
        <span class="input-icon">👤</span>
      </div>
    </div>
    <div class="form-group">
      <label for="password">Password</label>
      <div class="input-wrap">
        <input class="form-input" id="password" name="password" type="password"
               placeholder="Enter your password" autocomplete="current-password" required />
        <span class="input-icon">🔒</span>
        <button type="button" class="pw-toggle" onclick="togglePw()" id="pw-toggle" tabindex="-1">👁</button>
      </div>
    </div>
    <button type="submit" class="submit-btn" id="submit-btn">Sign In</button>
  </form>
  <div class="divider">or</div>
  <button class="submit-btn" type="button" onclick="showSignup()"
    style="background:var(--input-bg);color:var(--text);border:1.5px solid var(--input-border);box-shadow:none">
    ✨ Create an account
  </button>
  <div class="login-footer">
    Trial Doc v1.0 &middot; RAG-Powered Clinical Document Generation<br/>
    <a href="/docs" target="_blank">API Docs</a> &nbsp;&middot;&nbsp;
    <a href="/redoc" target="_blank">ReDoc</a>
  </div>
</div>
<!-- Sign-up card (hidden by default) -->
<div class="login-card" id="signup-panel" style="display:none">
  <div class="logo">
    <div class="logo-icon">✨</div>
    <div class="logo-text"><span>Create Account</span></div>
    <div class="logo-sub">Register for document generation access. Admin access is team-provisioned.</div>
  </div>
  <div class="error-msg" id="signup-error-msg"></div>
  <form id="signup-form" autocomplete="off">
    <div class="form-group">
      <label for="s-fullname">Full Name</label>
      <div class="input-wrap">
        <input class="form-input" id="s-fullname" type="text" placeholder="John Doe" autocomplete="name"/>
        <span class="input-icon">📝</span>
      </div>
    </div>
    <div class="form-group">
      <label for="s-email">Email</label>
      <div class="input-wrap">
        <input class="form-input" id="s-email" type="email" placeholder="john@example.com" autocomplete="email"/>
        <span class="input-icon">📧</span>
      </div>
    </div>
    <div class="form-group">
      <label for="s-username">Username *</label>
      <div class="input-wrap">
        <input class="form-input" id="s-username" type="text" placeholder="Min 3 characters" autocomplete="username" required/>
        <span class="input-icon">👤</span>
      </div>
    </div>
    <div class="form-group">
      <label for="s-password">Password *</label>
      <div class="input-wrap">
        <input class="form-input" id="s-password" type="password" placeholder="Min 6 characters" autocomplete="new-password" required/>
        <span class="input-icon">🔒</span>
      </div>
    </div>
    <div class="form-group">
      <label for="s-confirm">Confirm Password *</label>
      <div class="input-wrap">
        <input class="form-input" id="s-confirm" type="password" placeholder="Re-enter password" autocomplete="new-password" required/>
        <span class="input-icon">🔒</span>
      </div>
    </div>
    <button type="submit" class="submit-btn" id="signup-btn"
      style="background:linear-gradient(135deg,var(--success),var(--accent))">Create Account</button>
  </form>
  <div class="divider">or</div>
  <button class="submit-btn" type="button" onclick="showLogin()"
    style="background:var(--input-bg);color:var(--text);border:1.5px solid var(--input-border);box-shadow:none">
    ← Back to Sign In
  </button>
</div>
<script>
function getSavedThemeName() {
  try { return localStorage.getItem('ctdgen-theme') === 'light' ? 'light' : 'dark'; }
  catch { return 'dark'; }
}
function applyThemeName(name) {
  const isLight = name === 'light';
  document.documentElement.setAttribute('data-theme', isLight ? 'light' : 'dark');
  const btn = document.getElementById('theme-toggle');
  if (btn) {
    btn.textContent = isLight ? '☾' : '☀';
    btn.title = isLight ? 'Switch to dark mode' : 'Switch to light mode';
    btn.setAttribute('aria-label', btn.title);
  }
}
function toggleTheme() {
  const next = getSavedThemeName() === 'dark' ? 'light' : 'dark';
  try { localStorage.setItem('ctdgen-theme', next); } catch {}
  applyThemeName(next);
}
function togglePw() {
  const inp = document.getElementById('password');
  const btn = document.getElementById('pw-toggle');
  if (inp.type === 'password') { inp.type = 'text'; btn.textContent = '🙈'; }
  else { inp.type = 'password'; btn.textContent = '👁'; }
}
function showError(msg, id) {
  const el = document.getElementById(id || 'error-msg');
  el.textContent = msg;
  el.style.display = 'block';
  el.style.animation = 'none';
  el.offsetHeight;
  el.style.animation = 'shake 0.35s ease';
}
function showSignup() {
  document.getElementById('login-panel').style.display = 'none';
  document.getElementById('signup-panel').style.display = 'block';
  document.getElementById('signup-panel').style.animation = 'cardIn 0.4s ease-out';
  document.getElementById('s-fullname').focus();
}
function showLogin() {
  document.getElementById('signup-panel').style.display = 'none';
  document.getElementById('login-panel').style.display = 'block';
  document.getElementById('login-panel').style.animation = 'cardIn 0.4s ease-out';
  document.getElementById('username').focus();
}
// Login form
document.getElementById('login-form').addEventListener('submit', async (e) => {
  e.preventDefault();
  const btn = document.getElementById('submit-btn');
  const username = document.getElementById('username').value.trim();
  const password = document.getElementById('password').value;
  if (!username || !password) { showError('Please enter both username and password'); return; }
  btn.disabled = true;
  btn.innerHTML = '<span class="spinner"></span> Signing in…';
  document.getElementById('error-msg').style.display = 'none';
  try {
    const r = await fetch('/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password }),
    });
    const data = await r.json();
    if (!r.ok) throw new Error(data.detail || 'Login failed');
    btn.innerHTML = '✓ Redirecting…';
    btn.style.background = 'var(--success)';
    setTimeout(() => { window.location.href = data.redirect; }, 400);
  } catch (err) {
    showError(err.message);
    btn.disabled = false;
    btn.innerHTML = 'Sign In';
  }
});
// Signup form
document.getElementById('signup-form').addEventListener('submit', async (e) => {
  e.preventDefault();
  const btn = document.getElementById('signup-btn');
  const username = document.getElementById('s-username').value.trim();
  const password = document.getElementById('s-password').value;
  const confirm  = document.getElementById('s-confirm').value;
  const full_name = document.getElementById('s-fullname').value.trim();
  const email = document.getElementById('s-email').value.trim();
  document.getElementById('signup-error-msg').style.display = 'none';
  if (password !== confirm) { showError('Passwords do not match', 'signup-error-msg'); return; }
  if (username.length < 3) { showError('Username must be at least 3 characters', 'signup-error-msg'); return; }
  if (password.length < 6) { showError('Password must be at least 6 characters', 'signup-error-msg'); return; }
  btn.disabled = true;
  btn.innerHTML = '<span class="spinner"></span> Creating account…';
  try {
    const r = await fetch('/auth/signup', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password, full_name, email }),
    });
    const data = await r.json();
    if (!r.ok) throw new Error(data.detail || 'Registration failed');
    btn.innerHTML = '✓ Account created! Redirecting…';
    btn.style.background = 'var(--success)';
    setTimeout(() => { window.location.href = data.redirect; }, 500);
  } catch (err) {
    showError(err.message, 'signup-error-msg');
    btn.disabled = false;
    btn.innerHTML = 'Create Account';
  }
});
applyThemeName(getSavedThemeName());
document.getElementById('username').focus();
</script>
</body>
</html>"""
