"""
backend/api/admin_ui_html.py
Self-contained HTML/CSS/JS admin dashboard.
Served at http://localhost:8765/admin/ui
No build step required — pure vanilla JS calling the /admin/* REST endpoints.
"""

ADMIN_UI_HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<link rel="icon" type="image/png" href="/admin/favicon.png" />
<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
<title>Trial Doc Admin</title>
<style>
  :root {
    --bg:       #0B0F19;
    --surface:  #111827;
    --elevated: #1A2236;
    --overlay:  #1E2A40;
    --border:   #263347;
    --border2:  #2E3E56;
    --text:     #F0F4FF;
    --text2:    #A8B4CC;
    --muted:    #5C6E8A;
    --accent:   #20BEFF;
    --success:  #00C48C;
    --warning:  #FFB020;
    --danger:   #FF5C5C;
    --radius:   8px;
    --radius-lg:12px;
    font-family: 'Inter', 'Segoe UI', system-ui, sans-serif;
    font-size: 14px;
    color-scheme: dark;
  }
  :root[data-theme="light"] {
    --bg:       #EAF7FF;
    --surface:  #F8FCFF;
    --elevated: #DDF1FC;
    --overlay:  #CBE7F7;
    --border:   #D1DCF0;
    --border2:  #B8CADE;
    --text:     #0D1B2E;
    --text2:    #3A5068;
    --muted:    #7A90A8;
    --accent:   #0099D8;
    --success:  #00A572;
    --warning:  #D97706;
    --danger:   #DC2626;
    color-scheme: light;
  }
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { background: var(--bg); color: var(--text); height: 100vh; display: flex; overflow: hidden; }

  /* ── Sidebar ── */
  #sidebar {
    width: 220px; flex-shrink: 0;
    background: var(--surface);
    border-right: 1px solid var(--border);
    display: flex; flex-direction: column;
    overflow-y: auto;
  }
  .sidebar-logo {
    padding: 16px 16px 14px;
    border-bottom: 1px solid var(--border);
    display: flex; align-items: center; gap: 10px;
  }
  .brand-mark {
    width: 32px; height: 32px; flex-shrink: 0;
    display: flex; align-items: center; justify-content: center;
    overflow: hidden; border-radius: var(--radius);
    background: #fff; border: 1px solid rgba(13,27,46,.14);
    box-shadow: 0 8px 22px rgba(0,0,0,.14);
  }
  .brand-mark img { width: 34px; height: 34px; object-fit: cover; display: block; }
  .brand-copy { min-width: 0; overflow: hidden; }
  .brand-title { font-weight: 700; font-size: 14px; color: var(--text); line-height: 1.2; white-space: nowrap; }
  .brand-subtitle {
    color: var(--muted); font-weight: 600; font-size: 9px; display: block; margin-top: 2px;
    text-transform: uppercase; letter-spacing: .08em; white-space: nowrap;
  }
  .nav-section { padding: 10px 10px 4px; font-size: 10px; font-weight: 600; color: var(--muted); text-transform: uppercase; letter-spacing: .08em; }
  .nav-item {
    display: flex; align-items: center; gap: 9px;
    padding: 8px 12px; border-radius: var(--radius);
    margin: 1px 6px; cursor: pointer;
    font-size: 13px; color: var(--text2);
    transition: background .12s, color .12s;
    border: 1px solid transparent;
  }
  .nav-item:hover { background: var(--elevated); color: var(--text); }
  .nav-item.active { background: rgba(32,190,255,.1); color: var(--accent); border-color: rgba(32,190,255,.2); }
  .nav-icon { font-size: 15px; width: 18px; text-align: center; }

  /* ── Main area ── */
  #main { flex: 1; display: flex; flex-direction: column; overflow: hidden; }
  #topbar {
    padding: 14px 24px; background: var(--surface);
    border-bottom: 1px solid var(--border);
    display: flex; align-items: center; justify-content: space-between;
    flex-shrink: 0;
  }
  #topbar h1 { font-size: 16px; font-weight: 600; }
  #topbar .subtitle { font-size: 12px; color: var(--muted); margin-top: 2px; }
  #status-pill {
    display: inline-flex; align-items: center; gap: 6px;
    padding: 4px 10px; border-radius: 20px; font-size: 11px; font-weight: 500;
    background: rgba(0,196,140,.12); color: var(--success); border: 1px solid rgba(0,196,140,.25);
  }
  .topbar-actions { display: flex; align-items: center; gap: 10px; }
  .theme-toggle {
    width: 34px; height: 34px; flex-shrink: 0;
    display: inline-flex; align-items: center; justify-content: center;
    background: var(--elevated); color: var(--warning);
    border: 1px solid var(--border); border-radius: var(--radius);
    cursor: pointer; transition: background .15s, border-color .15s, color .15s, transform .15s;
    font-size: 16px; line-height: 1;
  }
  :root[data-theme="light"] .theme-toggle { color: var(--accent); }
  .theme-toggle:hover { background: var(--overlay); border-color: var(--border2); transform: scale(1.06); }
  #content { flex: 1; overflow-y: auto; padding: 24px; }

  /* ── Toast ── */
  #toast-container { position: fixed; top: 16px; right: 16px; z-index: 9999; display: flex; flex-direction: column; gap: 8px; }
  .toast {
    padding: 10px 16px; border-radius: var(--radius); font-size: 13px; font-weight: 500;
    border: 1px solid; min-width: 240px; max-width: 360px;
    animation: slideIn .2s ease;
  }
  .toast.success { background: rgba(0,196,140,.15); color: var(--success); border-color: rgba(0,196,140,.3); }
  .toast.error   { background: rgba(255,92,92,.15);  color: var(--danger);  border-color: rgba(255,92,92,.3); }
  .toast.info    { background: rgba(32,190,255,.12); color: var(--accent);  border-color: rgba(32,190,255,.25); }
  @keyframes slideIn { from { opacity:0; transform: translateX(16px); } to { opacity:1; transform:none; } }

  /* ── Cards & layout ── */
  .card { background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius-lg); padding: 18px; margin-bottom: 16px; }
  .card-title { font-size: 13px; font-weight: 600; color: var(--text); margin-bottom: 14px; display: flex; align-items: center; gap: 8px; }
  .card-subtitle { font-size: 11px; color: var(--muted); font-weight: 400; margin-left: auto; }
  .grid2 { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
  .grid3 { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 10px; }
  .flex-row { display: flex; align-items: center; gap: 8px; }
  .spacer { flex: 1; }

  /* ── Stat card ── */
  .stat { background: var(--elevated); border: 1px solid var(--border); border-radius: var(--radius); padding: 14px 16px; }
  .stat-value { font-size: 26px; font-weight: 700; letter-spacing: -0.03em; line-height: 1; }
  .stat-label { font-size: 11px; color: var(--muted); text-transform: uppercase; letter-spacing: .06em; margin-top: 4px; }

  /* ── Forms ── */
  label { font-size: 12px; font-weight: 500; color: var(--text2); display: block; margin-bottom: 5px; }
  input, textarea, select {
    width: 100%; padding: 8px 10px;
    background: var(--elevated); border: 1.5px solid var(--border);
    border-radius: var(--radius); color: var(--text); font-size: 13px;
    font-family: inherit; outline: none; transition: border-color .15s;
  }
  input:focus, textarea:focus, select:focus { border-color: var(--accent); box-shadow: 0 0 0 3px rgba(32,190,255,.1); }
  textarea { resize: vertical; min-height: 90px; line-height: 1.6; }
  .form-group { margin-bottom: 12px; }
  select option { background: var(--elevated); }

  /* ── Buttons ── */
  .btn {
    display: inline-flex; align-items: center; gap: 6px;
    padding: 7px 14px; border-radius: var(--radius); border: none;
    font-size: 12px; font-weight: 500; cursor: pointer; transition: all .15s;
    white-space: nowrap;
  }
  .btn-primary  { background: var(--accent); color: #000; }
  .btn-primary:hover  { opacity: .85; }
  .btn-success  { background: var(--success); color: #000; }
  .btn-success:hover  { opacity: .85; }
  .btn-danger   { background: rgba(255,92,92,.15); color: var(--danger); border: 1px solid rgba(255,92,92,.3); }
  .btn-danger:hover   { background: rgba(255,92,92,.25); }
  .btn-ghost    { background: var(--elevated); color: var(--text2); border: 1px solid var(--border); }
  .btn-ghost:hover    { background: var(--overlay); color: var(--text); }
  .btn-warning  { background: rgba(255,176,32,.15); color: var(--warning); border: 1px solid rgba(255,176,32,.3); }
  .btn-warning:hover  { background: rgba(255,176,32,.25); }
  .btn:disabled { opacity: .45; cursor: not-allowed; }

  /* ── Table ── */
  .table-wrap { overflow-x: auto; }
  table { width: 100%; border-collapse: collapse; font-size: 12px; }
  thead tr { background: var(--overlay); }
  th { padding: 8px 12px; text-align: left; font-weight: 600; font-size: 11px; color: var(--muted); text-transform: uppercase; letter-spacing: .06em; border-bottom: 1px solid var(--border); }
  td { padding: 9px 12px; color: var(--text2); border-bottom: 1px solid var(--border); vertical-align: top; }
  tr:last-child td { border-bottom: none; }
  tr:hover td { background: var(--elevated); }

  /* ── Tags / Badges ── */
  .badge { display: inline-flex; align-items: center; padding: 2px 7px; border-radius: 99px; font-size: 10px; font-weight: 600; }
  .badge-critical { background: rgba(255,92,92,.15);  color: var(--danger);  border: 1px solid rgba(255,92,92,.3); }
  .badge-warning  { background: rgba(255,176,32,.15); color: var(--warning); border: 1px solid rgba(255,176,32,.3); }
  .badge-info     { background: rgba(32,190,255,.12); color: var(--accent);  border: 1px solid rgba(32,190,255,.25); }
  .badge-success  { background: rgba(0,196,140,.12);  color: var(--success); border: 1px solid rgba(0,196,140,.25); }

  /* ── Accordion item ── */
  .accordion { background: var(--elevated); border: 1px solid var(--border); border-radius: var(--radius); margin-bottom: 6px; overflow: hidden; }
  .accordion-header { padding: 10px 14px; cursor: pointer; display: flex; align-items: center; gap: 8px; font-size: 13px; font-weight: 500; user-select: none; }
  .accordion-header:hover { background: var(--overlay); }
  .accordion-body { padding: 0 14px 14px; display: none; }
  .accordion.open .accordion-body { display: block; }
  .accordion-chevron { margin-left: auto; font-size: 11px; transition: transform .15s; color: var(--muted); }
  .accordion.open .accordion-chevron { transform: rotate(180deg); }

  /* ── Page sections ── */
  .page { display: none; }
  .page.active { display: block; }

  /* ── Code block ── */
  code { font-family: 'JetBrains Mono', 'Fira Code', monospace; font-size: 11px; background: var(--overlay); padding: 1px 5px; border-radius: 4px; color: var(--accent); }
  pre { background: var(--overlay); border: 1px solid var(--border); border-radius: var(--radius); padding: 14px; overflow-x: auto; font-size: 11px; line-height: 1.7; color: var(--text2); }

  /* ── Drag handle ── */
  .drag-handle { cursor: grab; color: var(--muted); padding: 0 6px; font-size: 13px; }
  .drag-handle:active { cursor: grabbing; }
  .sortable-ghost { opacity: .4; background: var(--overlay); }

  /* ── Empty state ── */
  .empty { text-align: center; padding: 40px 20px; color: var(--muted); font-size: 13px; }
  .empty-icon { font-size: 36px; margin-bottom: 10px; opacity: .4; }

  /* ── Scrollbar ── */
  ::-webkit-scrollbar { width: 4px; height: 4px; }
  ::-webkit-scrollbar-track { background: transparent; }
  ::-webkit-scrollbar-thumb { background: var(--border2); border-radius: 99px; }

  /* ── Confirm modal ── */
  .modal-backdrop { position: fixed; inset: 0; background: rgba(0,0,0,.6); z-index: 500; display: none; align-items: center; justify-content: center; }
  .modal-backdrop.open { display: flex; }
  .modal { background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius-lg); padding: 24px; width: 380px; max-width: 90vw; }
  .modal h3 { font-size: 15px; margin-bottom: 8px; }
  .modal p { font-size: 13px; color: var(--text2); margin-bottom: 20px; line-height: 1.5; }
  .modal-btns { display: flex; gap: 8px; justify-content: flex-end; }

  hr { border: none; border-top: 1px solid var(--border); margin: 16px 0; }
</style>
</head>
<body>

<!-- ── SIDEBAR ──────────────────────────────────────────────────────────────── -->
<nav id="sidebar">
  <div class="sidebar-logo">
    <div class="brand-mark"><img src="/admin/logo.png" alt="Circulants AI"></div>
    <div class="brand-copy">
      <div class="brand-title">TrialDoc Admin</div>
      <div class="brand-subtitle">AI Generator</div>
    </div>
  </div>

  <div class="nav-section">Overview</div>
  <div class="nav-item active" onclick="showPage('dashboard')">
    <span class="nav-icon">📊</span> Dashboard
  </div>

  <div class="nav-section">Document Structure</div>
  <div class="nav-item" onclick="showPage('section-map')">
    <span class="nav-icon">📋</span> Section Map
  </div>
  <div class="nav-item" onclick="showPage('section-prompts')">
    <span class="nav-icon">🤖</span> AI System Prompts
  </div>

  <div class="nav-section">Compliance</div>
  <div class="nav-item" onclick="showPage('compliance-rules')">
    <span class="nav-icon">🛡</span> Compliance Rules
  </div>
  <div class="nav-item" onclick="showPage('guidelines')">
    <span class="nav-icon">📜</span> Regulatory Guidelines
  </div>
  <div class="nav-item" onclick="showPage('phase-guidelines')">
    <span class="nav-icon">🔬</span> Phase Guidelines
  </div>

  <div class="nav-section">System</div>
  <div class="nav-item" onclick="showPage('api-explorer')">
    <span class="nav-icon">🔌</span> API Explorer
  </div>
  <div class="nav-item" onclick="showPage('reset')">
    <span class="nav-icon">↺</span> Reset / Export
  </div>

  <div style="flex:1"></div>
  <div style="padding:12px 16px; font-size:10px; color:var(--muted); border-top:1px solid var(--border)">
    🌐 <a href="/docs" target="_blank" style="color:var(--accent); text-decoration:none">Swagger UI</a> &nbsp;·&nbsp;
    <a href="/redoc" target="_blank" style="color:var(--accent); text-decoration:none">ReDoc</a>
    <div style="margin-top:8px">
      <button onclick="fetch('/auth/logout',{method:'POST'}).then(()=>window.location.href='/login')"
              style="background:rgba(255,92,92,0.12);color:#FF5C5C;border:1px solid rgba(255,92,92,0.25);
                     border-radius:6px;padding:5px 12px;font-size:11px;cursor:pointer;width:100%;
                     font-family:inherit;transition:background 0.15s">
        ↩ Sign Out
      </button>
    </div>
  </div>
</nav>

<!-- ── MAIN ──────────────────────────────────────────────────────────────────── -->
<div id="main">
  <div id="topbar">
    <div>
      <h1 id="page-title">Dashboard</h1>
      <div class="subtitle" id="page-subtitle">System overview and quick stats</div>
    </div>
    <div class="topbar-actions">
      <button class="theme-toggle" id="theme-toggle" type="button"
              onclick="toggleTheme()" title="Switch to light mode"
              aria-label="Switch to light mode">☀</button>
      <div id="status-pill">● API Online · localhost:8765</div>
    </div>
  </div>

  <div id="content">

    <!-- ══════════════════════════════════════════════════════════════════════ -->
    <!-- DASHBOARD                                                              -->
    <!-- ══════════════════════════════════════════════════════════════════════ -->
    <div class="page active" id="page-dashboard">
      <div class="grid3" id="dashboard-stats">
        <div class="stat"><div class="stat-value" style="color:var(--accent)" id="stat-doctypes">—</div><div class="stat-label">Document Types</div></div>
        <div class="stat"><div class="stat-value" style="color:var(--success)" id="stat-sections">—</div><div class="stat-label">Total Sections</div></div>
        <div class="stat"><div class="stat-value" style="color:var(--warning)" id="stat-rules">—</div><div class="stat-label">Compliance Rules</div></div>
      </div>

      <div class="card" style="margin-top:16px">
        <div class="card-title">📋 Document Types & Sections</div>
        <div class="table-wrap">
          <table>
            <thead><tr><th>Document Type</th><th>Sections</th><th>Guidelines</th><th>Rules</th></tr></thead>
            <tbody id="dashboard-table"><tr><td colspan="4" class="empty">Loading…</td></tr></tbody>
          </table>
        </div>
      </div>

      <div class="card">
        <div class="card-title">⚡ Quick Actions</div>
        <div class="flex-row" style="flex-wrap:wrap; gap:8px">
          <button class="btn btn-primary" onclick="showPage('section-map')">📋 Manage Sections</button>
          <button class="btn btn-ghost"   onclick="showPage('section-prompts')">🤖 Edit AI Prompts</button>
          <button class="btn btn-ghost"   onclick="showPage('compliance-rules')">🛡 Edit Rules</button>
          <button class="btn btn-ghost"   onclick="showPage('guidelines')">📜 Edit Guidelines</button>
          <button class="btn btn-warning" onclick="showPage('reset')">↺ Reset Overrides</button>
        </div>
      </div>

      <div class="card">
        <div class="card-title">🔗 Useful Links</div>
        <div class="flex-row" style="flex-wrap:wrap;gap:8px;font-size:13px;color:var(--text2)">
          <a href="/docs"       target="_blank" class="btn btn-ghost">📖 Swagger UI</a>
          <a href="/api/v1/health"   target="_blank" class="btn btn-ghost">💊 Health Check</a>
          <a href="/api/v1/templates" target="_blank" class="btn btn-ghost">📑 Templates API</a>
        </div>
      </div>
    </div>


    <!-- ══════════════════════════════════════════════════════════════════════ -->
    <!-- SECTION MAP                                                            -->
    <!-- ══════════════════════════════════════════════════════════════════════ -->
    <div class="page" id="page-section-map">

      <!-- Select document type -->
      <div class="card">
        <div class="card-title">📋 Section Map Editor</div>
        <div class="flex-row">
          <div style="flex:1" class="form-group" style="margin:0">
            <label>Document Type</label>
            <select id="sm-doctype-select" onchange="loadSectionMap()"></select>
          </div>
          <div style="margin-top:18px; display:flex; gap:8px">
            <button class="btn btn-ghost" onclick="openNewDocTypeModal()">+ New Type</button>
            <button class="btn btn-danger" onclick="deleteDocType()" id="sm-delete-doctype-btn">🗑 Delete Type</button>
          </div>
        </div>
      </div>

      <!-- Sections list -->
      <div class="card">
        <div class="card-title">
          Sections
          <span class="card-subtitle" id="sm-section-count"></span>
          <button class="btn btn-primary" onclick="openAddSectionModal()" style="margin-left:auto">+ Add Section</button>
        </div>
        <div class="table-wrap">
          <table>
            <thead><tr><th>Order</th><th>Section ID</th><th>Display Title</th><th>System Prompt</th><th>Actions</th></tr></thead>
            <tbody id="sm-sections-table"><tr><td colspan="5" class="empty">Select a document type</td></tr></tbody>
          </table>
        </div>
      </div>
    </div>


    <!-- ══════════════════════════════════════════════════════════════════════ -->
    <!-- SECTION AI PROMPTS                                                    -->
    <!-- ══════════════════════════════════════════════════════════════════════ -->
    <div class="page" id="page-section-prompts">
      <div class="card">
        <div class="card-title">🤖 AI System Prompts</div>
        <p style="font-size:12px;color:var(--muted);margin-bottom:14px">
          Each section has a system prompt that shapes the AI persona. Edits here persist across restarts.<br>
          Click a section to expand and edit. Changes apply to all new generations immediately.
        </p>
        <div id="sp-list">Loading…</div>
      </div>
    </div>


    <!-- ══════════════════════════════════════════════════════════════════════ -->
    <!-- COMPLIANCE RULES                                                      -->
    <!-- ══════════════════════════════════════════════════════════════════════ -->
    <div class="page" id="page-compliance-rules">
      <div class="card">
        <div class="card-title">🛡 Compliance Rules</div>
        <div class="flex-row">
          <div style="flex:1" class="form-group" style="margin:0">
            <label>Document Type</label>
            <select id="cr-doctype-select" onchange="loadComplianceRules()"></select>
          </div>
          <div style="margin-top:18px">
            <button class="btn btn-primary" onclick="openAddRuleModal()">+ Add Rule</button>
          </div>
        </div>
      </div>

      <div class="card">
        <div class="card-title">
          Rules
          <span class="card-subtitle" id="cr-rule-count"></span>
        </div>
        <div class="table-wrap">
          <table>
            <thead><tr><th>ID</th><th>Severity</th><th>Pattern</th><th>Description</th><th>Fix</th><th>Ref</th><th>Actions</th></tr></thead>
            <tbody id="cr-rules-table"><tr><td colspan="7" class="empty">Select a document type</td></tr></tbody>
          </table>
        </div>
      </div>
    </div>


    <!-- ══════════════════════════════════════════════════════════════════════ -->
    <!-- REGULATORY GUIDELINES                                                 -->
    <!-- ══════════════════════════════════════════════════════════════════════ -->
    <div class="page" id="page-guidelines">
      <div class="card">
        <div class="card-title">📜 Regulatory Guidelines</div>
        <p style="font-size:12px;color:var(--muted);margin-bottom:14px">
          These guidelines are injected into LLM prompts as reference context during document generation.
          Expand each document type to view and edit its guidelines.
        </p>

        <div class="flex-row" style="margin-bottom:14px">
          <select id="gl-doctype-select" style="max-width:260px" onchange="loadGuidelines()"></select>
          <button class="btn btn-primary" onclick="openAddGuidelineModal()" style="margin-left:8px">+ Add Guideline</button>
        </div>

        <div id="gl-list">Loading…</div>
      </div>
    </div>


    <!-- ══════════════════════════════════════════════════════════════════════ -->
    <!-- PHASE GUIDELINES                                                      -->
    <!-- ══════════════════════════════════════════════════════════════════════ -->
    <div class="page" id="page-phase-guidelines">
      <div class="card">
        <div class="card-title">🔬 Phase-Specific Guidelines</div>
        <p style="font-size:12px;color:var(--muted);margin-bottom:14px">
          These guidelines are appended to prompts based on the study phase selected by the user.
        </p>
        <button class="btn btn-primary" onclick="openAddPhaseModal()" style="margin-bottom:14px">+ Add Phase</button>
        <div id="pg-list">Loading…</div>
      </div>
    </div>


    <!-- ══════════════════════════════════════════════════════════════════════ -->
    <!-- API EXPLORER                                                          -->
    <!-- ══════════════════════════════════════════════════════════════════════ -->
    <div class="page" id="page-api-explorer">
      <div class="card">
        <div class="card-title">🔌 Admin API Explorer</div>
        <p style="font-size:12px;color:var(--muted);margin-bottom:16px">
          All admin endpoints listed below. Click to expand and test directly.
        </p>

        <div id="api-list"></div>
      </div>
    </div>


    <!-- ══════════════════════════════════════════════════════════════════════ -->
    <!-- RESET / EXPORT                                                        -->
    <!-- ══════════════════════════════════════════════════════════════════════ -->
    <div class="page" id="page-reset">
      <div class="card">
        <div class="card-title" style="color:var(--warning)">↺ Reset Overrides</div>
        <p style="font-size:13px;color:var(--text2);margin-bottom:16px;line-height:1.6">
          All your edits are stored in <code>backend/db/admin_overrides.json</code> and layered on top of
          the source Python files. Resetting removes overrides and restores the original source defaults.
          The source files themselves are never modified.
        </p>
        <div class="grid2" style="gap:12px">
          <div class="card" style="border-color:var(--border2)">
            <div style="font-size:13px;font-weight:600;margin-bottom:6px">Reset Section Map</div>
            <div style="font-size:12px;color:var(--muted);margin-bottom:12px">Restores all document types and section orders to defaults.</div>
            <button class="btn btn-warning" onclick="resetKey('section_map')">Reset Section Map</button>
          </div>
          <div class="card" style="border-color:var(--border2)">
            <div style="font-size:13px;font-weight:600;margin-bottom:6px">Reset AI Prompts</div>
            <div style="font-size:12px;color:var(--muted);margin-bottom:12px">Restores all per-section LLM system prompts to defaults.</div>
            <button class="btn btn-warning" onclick="resetKey('section_systems')">Reset Prompts</button>
          </div>
          <div class="card" style="border-color:var(--border2)">
            <div style="font-size:13px;font-weight:600;margin-bottom:6px">Reset Compliance Rules</div>
            <div style="font-size:12px;color:var(--muted);margin-bottom:12px">Restores all compliance rules to defaults.</div>
            <button class="btn btn-warning" onclick="resetKey('compliance_rules')">Reset Rules</button>
          </div>
          <div class="card" style="border-color:var(--border2)">
            <div style="font-size:13px;font-weight:600;margin-bottom:6px">Reset Guidelines</div>
            <div style="font-size:12px;color:var(--muted);margin-bottom:12px">Restores regulatory and phase guidelines to defaults.</div>
            <button class="btn btn-warning" onclick="resetKey('regulatory_guidelines'); resetKey('phase_guidelines')">Reset Guidelines</button>
          </div>
        </div>
        <hr>
        <div class="card" style="border-color:rgba(255,92,92,.3)">
          <div style="font-size:13px;font-weight:600;color:var(--danger);margin-bottom:6px">🗑 Reset ALL Overrides</div>
          <div style="font-size:12px;color:var(--muted);margin-bottom:12px">Deletes the entire overrides file. All settings revert to source defaults.</div>
          <button class="btn btn-danger" onclick="resetAll()">Reset Everything</button>
        </div>
      </div>

      <div class="card">
        <div class="card-title">📦 Export Overrides</div>
        <p style="font-size:12px;color:var(--muted);margin-bottom:12px">Download the current overrides file as JSON for backup or version control.</p>
        <button class="btn btn-ghost" onclick="exportOverrides()">⬇ Download admin_overrides.json</button>
      </div>
    </div>

  </div><!-- end #content -->
</div><!-- end #main -->


<!-- ══════════════════════════════════════════════════════════════════════════ -->
<!-- MODALS                                                                    -->
<!-- ══════════════════════════════════════════════════════════════════════════ -->

<!-- Generic confirm modal -->
<div class="modal-backdrop" id="confirm-modal">
  <div class="modal">
    <h3 id="confirm-title">Confirm Action</h3>
    <p id="confirm-body">Are you sure?</p>
    <div class="modal-btns">
      <button class="btn btn-ghost" onclick="closeModal('confirm-modal')">Cancel</button>
      <button class="btn btn-danger" id="confirm-ok-btn">Confirm</button>
    </div>
  </div>
</div>

<!-- New document type -->
<div class="modal-backdrop" id="newdoctype-modal">
  <div class="modal">
    <h3>New Document Type</h3>
    <div class="form-group" style="margin:16px 0">
      <label>Document Type Name</label>
      <input id="newdoctype-input" placeholder="e.g. Risk Management Plan" />
    </div>
    <div class="modal-btns">
      <button class="btn btn-ghost" onclick="closeModal('newdoctype-modal')">Cancel</button>
      <button class="btn btn-primary" onclick="createDocType()">Create</button>
    </div>
  </div>
</div>

<!-- Add / edit section -->
<div class="modal-backdrop" id="section-modal">
  <div class="modal" style="width:480px;max-width:95vw">
    <h3 id="section-modal-title">Add Section</h3>
    <div style="margin:14px 0; display:flex;flex-direction:column;gap:10px">
      <div class="form-group">
        <label>Section ID <code>snake_case</code></label>
        <input id="sm-sid-input" placeholder="e.g. risk_management" />
      </div>
      <div class="form-group">
        <label>Display Title</label>
        <input id="sm-stitle-input" placeholder="e.g. 10. Risk Management" />
      </div>
    </div>
    <div class="modal-btns">
      <button class="btn btn-ghost" onclick="closeModal('section-modal')">Cancel</button>
      <button class="btn btn-primary" id="section-modal-ok" onclick="saveSection()">Add Section</button>
    </div>
  </div>
</div>

<!-- Edit system prompt -->
<div class="modal-backdrop" id="prompt-modal">
  <div class="modal" style="width:600px;max-width:95vw">
    <h3>Edit System Prompt — <span id="prompt-modal-sid"></span></h3>
    <div style="margin:14px 0">
      <label>System Prompt (instructions for the LLM when generating this section)</label>
      <textarea id="prompt-modal-text" style="min-height:200px;margin-top:6px"></textarea>
    </div>
    <div class="modal-btns">
      <button class="btn btn-ghost"    onclick="closeModal('prompt-modal')">Cancel</button>
      <button class="btn btn-warning"  onclick="resetPrompt()">Reset to Default</button>
      <button class="btn btn-primary"  onclick="savePrompt()">Save Prompt</button>
    </div>
  </div>
</div>

<!-- Add compliance rule -->
<div class="modal-backdrop" id="rule-modal">
  <div class="modal" style="width:580px;max-width:95vw">
    <h3 id="rule-modal-title">Add Compliance Rule</h3>
    <div style="margin:14px 0;display:flex;flex-direction:column;gap:10px">
      <div class="grid2">
        <div class="form-group">
          <label>Rule ID</label>
          <input id="rule-id" placeholder="e.g. CSP-011" />
        </div>
        <div class="form-group">
          <label>Severity</label>
          <select id="rule-severity">
            <option value="critical">🔴 Critical</option>
            <option value="warning" selected>🟡 Warning</option>
            <option value="info">🔵 Info</option>
          </select>
        </div>
      </div>
      <div class="form-group">
        <label>Regex Pattern (searched in section content)</label>
        <input id="rule-pattern" placeholder="e.g. stopping rule|discontinuation criteria" />
      </div>
      <div class="form-group">
        <label>Description (shown to reviewer)</label>
        <input id="rule-desc" placeholder="e.g. Stopping rules not specified" />
      </div>
      <div class="form-group">
        <label>Fix Suggestion</label>
        <input id="rule-fix" placeholder="e.g. Define criteria for study stopping" />
      </div>
      <div class="grid2">
        <div class="form-group">
          <label>Regulatory Reference</label>
          <input id="rule-ref" placeholder="e.g. ICH E6 §6.5.3" />
        </div>
        <div class="form-group">
          <label style="display:flex;align-items:center;gap:6px;margin-top:18px">
            <input type="checkbox" id="rule-required" checked style="width:auto;accent-color:var(--accent)"> Required
          </label>
        </div>
      </div>
    </div>
    <div class="modal-btns">
      <button class="btn btn-ghost" onclick="closeModal('rule-modal')">Cancel</button>
      <button class="btn btn-primary" id="rule-modal-ok" onclick="saveRule()">Add Rule</button>
    </div>
  </div>
</div>

<!-- Add guideline -->
<div class="modal-backdrop" id="guideline-modal">
  <div class="modal" style="width:580px;max-width:95vw">
    <h3>Add Guideline</h3>
    <div style="margin:14px 0;display:flex;flex-direction:column;gap:10px">
      <div class="form-group">
        <label>Guideline Name (e.g. ICH E6(R2), FDA 21 CFR 312)</label>
        <input id="gl-name-input" placeholder="e.g. EMA Guideline on GCP" />
      </div>
      <div class="form-group">
        <label>Guideline Content (injected into LLM prompt)</label>
        <textarea id="gl-text-input" placeholder="Paste guideline text here..." style="min-height:160px"></textarea>
      </div>
    </div>
    <div class="modal-btns">
      <button class="btn btn-ghost" onclick="closeModal('guideline-modal')">Cancel</button>
      <button class="btn btn-primary" onclick="saveGuideline()">Add Guideline</button>
    </div>
  </div>
</div>

<!-- Add phase guideline -->
<div class="modal-backdrop" id="phase-modal">
  <div class="modal" style="width:580px;max-width:95vw">
    <h3 id="phase-modal-title">Add Phase Guideline</h3>
    <div style="margin:14px 0;display:flex;flex-direction:column;gap:10px">
      <div class="form-group">
        <label>Phase Key (e.g. Phase I, Phase III)</label>
        <input id="pg-key-input" placeholder="e.g. Phase IIb" />
      </div>
      <div class="form-group">
        <label>Guideline Content</label>
        <textarea id="pg-text-input" style="min-height:160px" placeholder="Phase-specific guidance injected into prompts..."></textarea>
      </div>
    </div>
    <div class="modal-btns">
      <button class="btn btn-ghost" onclick="closeModal('phase-modal')">Cancel</button>
      <button class="btn btn-primary" id="phase-modal-ok" onclick="savePhaseGuideline()">Save</button>
    </div>
  </div>
</div>

<!-- Toast container -->
<div id="toast-container"></div>


<!-- ══════════════════════════════════════════════════════════════════════════ -->
<!-- JAVASCRIPT                                                                -->
<!-- ══════════════════════════════════════════════════════════════════════════ -->
<script>
const BASE = '/admin';
let _overview = {};
let _currentDocType = null;
let _currentRuleEditId = null;
let _currentPromptSid  = null;
let _currentPhaseKey   = null;
let _editingSectionIdx = null;  // null = add new, number = editing existing

// ── Fetch helpers ────────────────────────────────────────────────────────────
async function api(method, path, body) {
  const opts = { method, headers: { 'Content-Type': 'application/json' } };
  if (body !== undefined) opts.body = JSON.stringify(body);
  const r = await fetch(BASE + path, opts);
  const data = await r.json().catch(() => ({}));
  if (!r.ok) throw new Error(data.detail || `HTTP ${r.status}`);
  return data;
}
const GET    = p     => api('GET',    p);
const POST   = (p,b) => api('POST',   p, b);
const PUT    = (p,b) => api('PUT',    p, b);
const DELETE = p     => api('DELETE', p);

// ── Toast ────────────────────────────────────────────────────────────────────
function toast(msg, type='info', ms=3000) {
  const el = document.createElement('div');
  el.className = `toast ${type}`;
  el.textContent = msg;
  document.getElementById('toast-container').appendChild(el);
  setTimeout(() => el.remove(), ms);
}

// ── Navigation ───────────────────────────────────────────────────────────────
const PAGE_TITLES = {
  dashboard:        ['Dashboard',              'System overview and quick stats'],
  'section-map':    ['Section Map',            'Define sections for each document type'],
  'section-prompts':['AI System Prompts',      'LLM persona per section'],
  'compliance-rules':['Compliance Rules',      'Regulatory validation patterns'],
  guidelines:       ['Regulatory Guidelines',  'Guideline text injected into LLM prompts'],
  'phase-guidelines':['Phase Guidelines',      'Phase-specific addendum guidelines'],
  'api-explorer':   ['API Explorer',           'Test admin endpoints directly'],
  reset:            ['Reset / Export',         'Restore defaults or export overrides'],
};

function showPage(id) {
  document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
  document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
  document.getElementById(`page-${id}`).classList.add('active');
  document.querySelectorAll('.nav-item').forEach(n => {
    if (n.getAttribute('onclick')?.includes(`'${id}'`)) n.classList.add('active');
  });
  const [t, s] = PAGE_TITLES[id] || [id, ''];
  document.getElementById('page-title').textContent = t;
  document.getElementById('page-subtitle').textContent = s;

  if (id === 'dashboard')         loadDashboard();
  if (id === 'section-map')       initSectionMap();
  if (id === 'section-prompts')   loadSectionPrompts();
  if (id === 'compliance-rules')  initComplianceRules();
  if (id === 'guidelines')        initGuidelines();
  if (id === 'phase-guidelines')  loadPhaseGuidelines();
  if (id === 'api-explorer')      renderApiExplorer();
}

// ── Modals ───────────────────────────────────────────────────────────────────
function openModal(id)  { document.getElementById(id).classList.add('open'); }
function closeModal(id) { document.getElementById(id).classList.remove('open'); }
document.querySelectorAll('.modal-backdrop').forEach(b => {
  b.addEventListener('click', e => { if (e.target === b) b.classList.remove('open'); });
});

function confirmAction(title, body, cb) {
  document.getElementById('confirm-title').textContent = title;
  document.getElementById('confirm-body').textContent  = body;
  document.getElementById('confirm-ok-btn').onclick = () => { closeModal('confirm-modal'); cb(); };
  openModal('confirm-modal');
}

// ══════════════════════════════════════════════════════════════════════════════
// DASHBOARD
// ══════════════════════════════════════════════════════════════════════════════
async function loadDashboard() {
  try {
    _overview = await GET('/overview');
    document.getElementById('stat-doctypes').textContent = _overview.document_types?.length || 0;
    document.getElementById('stat-sections').textContent = _overview.total_sections || 0;
    const ruleTotal = Object.values(_overview.compliance_rule_counts || {}).reduce((s,v)=>s+v,0);
    document.getElementById('stat-rules').textContent = ruleTotal;

    const tbody = document.getElementById('dashboard-table');
    tbody.innerHTML = (_overview.document_types || []).map(dt => `
      <tr>
        <td><strong>${dt}</strong></td>
        <td>${(_overview.section_map?.[dt] || []).length || '—'} sections</td>
        <td>${(_overview.guidelines_loaded?.[dt] || []).join(', ') || '—'}</td>
        <td>${_overview.compliance_rule_counts?.[dt] || 0} rules</td>
      </tr>
    `).join('') || '<tr><td colspan="4" class="empty">No data</td></tr>';
  } catch(e) { toast('Dashboard load failed: ' + e.message, 'error'); }
}

// ══════════════════════════════════════════════════════════════════════════════
// SECTION MAP
// ══════════════════════════════════════════════════════════════════════════════
async function initSectionMap() {
  try {
    const sm  = await GET('/section-map');
    const sel = document.getElementById('sm-doctype-select');
    const cur = sel.value;
    sel.innerHTML = Object.keys(sm).map(dt => `<option value="${dt}">${dt}</option>`).join('');
    if (cur && sm[cur]) sel.value = cur;
    _currentDocType = sel.value;
    loadSectionMap();
  } catch(e) { toast(e.message,'error'); }
}

async function loadSectionMap() {
  _currentDocType = document.getElementById('sm-doctype-select').value;
  if (!_currentDocType) return;
  try {
    const data = await GET(`/section-map/${encodeURIComponent(_currentDocType)}`);
    const sections = data.sections || [];
    document.getElementById('sm-section-count').textContent = `${sections.length} sections`;
    const ss = await GET('/section-systems');

    const tbody = document.getElementById('sm-sections-table');
    tbody.innerHTML = sections.length ? sections.map((s, i) => {
      const [sid, title] = s;
      const hasPrompt = !!ss[sid];
      return `
        <tr>
          <td style="color:var(--muted)">${i+1}</td>
          <td><code>${sid}</code></td>
          <td>${title}</td>
          <td>${hasPrompt ? '<span class="badge badge-success">Custom</span>' : '<span class="badge badge-info">Default</span>'}</td>
          <td>
            <div class="flex-row">
              <button class="btn btn-ghost" style="padding:4px 8px;font-size:11px" onclick="openEditSectionModal(${i},'${sid}','${title.replace(/'/g,"\\'")}')">✏ Edit</button>
              <button class="btn btn-ghost" style="padding:4px 8px;font-size:11px" onclick="editPromptFor('${sid}')">🤖 Prompt</button>
              <button class="btn btn-danger" style="padding:4px 8px;font-size:11px" onclick="deleteSection('${sid}')">🗑</button>
            </div>
          </td>
        </tr>`;
    }).join('') : '<tr><td colspan="5" class="empty">No sections defined</td></tr>';
  } catch(e) { toast(e.message,'error'); }
}

function openAddSectionModal() {
  _editingSectionIdx = null;
  document.getElementById('section-modal-title').textContent = 'Add Section';
  document.getElementById('section-modal-ok').textContent    = 'Add Section';
  document.getElementById('sm-sid-input').value   = '';
  document.getElementById('sm-stitle-input').value = '';
  openModal('section-modal');
}

function openEditSectionModal(idx, sid, title) {
  _editingSectionIdx = idx;
  document.getElementById('section-modal-title').textContent = 'Edit Section';
  document.getElementById('section-modal-ok').textContent    = 'Save Changes';
  document.getElementById('sm-sid-input').value    = sid;
  document.getElementById('sm-stitle-input').value = title;
  openModal('section-modal');
}

async function saveSection() {
  const sid   = document.getElementById('sm-sid-input').value.trim();
  const title = document.getElementById('sm-stitle-input').value.trim();
  if (!sid || !title) { toast('Both fields are required','error'); return; }
  try {
    if (_editingSectionIdx !== null) {
      // Build updated list and PUT
      const data = await GET(`/section-map/${encodeURIComponent(_currentDocType)}`);
      const sections = data.sections || [];
      sections[_editingSectionIdx] = [sid, title];
      await PUT(`/section-map/${encodeURIComponent(_currentDocType)}`, sections);
      toast('Section updated','success');
    } else {
      await POST(`/section-map/${encodeURIComponent(_currentDocType)}/sections`, [sid, title]);
      toast('Section added','success');
    }
    closeModal('section-modal');
    loadSectionMap();
  } catch(e) { toast(e.message,'error'); }
}

async function deleteSection(sid) {
  confirmAction('Delete Section', `Remove section "${sid}" from "${_currentDocType}"?`, async () => {
    try {
      await DELETE(`/section-map/${encodeURIComponent(_currentDocType)}/sections/${sid}`);
      toast('Section removed','success');
      loadSectionMap();
    } catch(e) { toast(e.message,'error'); }
  });
}

function openNewDocTypeModal() {
  document.getElementById('newdoctype-input').value = '';
  openModal('newdoctype-modal');
}

async function createDocType() {
  const name = document.getElementById('newdoctype-input').value.trim();
  if (!name) { toast('Name required','error'); return; }
  try {
    await POST('/section-map/document-types', { doc_type: name });
    toast(`Created "${name}"`, 'success');
    closeModal('newdoctype-modal');
    initSectionMap();
  } catch(e) { toast(e.message,'error'); }
}

async function deleteDocType() {
  if (!_currentDocType) return;
  confirmAction('Delete Document Type', `Permanently remove "${_currentDocType}" and all its sections?`, async () => {
    try {
      await DELETE(`/section-map/document-types/${encodeURIComponent(_currentDocType)}`);
      toast('Document type deleted','success');
      initSectionMap();
    } catch(e) { toast(e.message,'error'); }
  });
}


// ══════════════════════════════════════════════════════════════════════════════
// SECTION PROMPTS
// ══════════════════════════════════════════════════════════════════════════════
async function loadSectionPrompts() {
  try {
    const [sm, ss] = await Promise.all([GET('/section-map'), GET('/section-systems')]);
    const allSids = [...new Set(Object.values(sm).flat().map(s => s[0]))];

    const container = document.getElementById('sp-list');
    container.innerHTML = allSids.map(sid => {
      const prompt = ss[sid] || '(using default — not overridden)';
      const isCustom = !!ss[sid];
      return `
        <div class="accordion" id="acc-${sid}">
          <div class="accordion-header" onclick="toggleAccordion('acc-${sid}')">
            <code>${sid}</code>
            ${isCustom ? '<span class="badge badge-success" style="margin-left:8px">Custom</span>' : '<span class="badge badge-info" style="margin-left:8px">Default</span>'}
            <span class="accordion-chevron">▼</span>
          </div>
          <div class="accordion-body">
            <pre style="margin-bottom:10px;white-space:pre-wrap">${escHtml(prompt)}</pre>
            <div class="flex-row">
              <button class="btn btn-primary" onclick="editPromptFor('${sid}')">✏ Edit Prompt</button>
              ${isCustom ? `<button class="btn btn-warning" onclick="resetSectionPrompt('${sid}')">↺ Reset to Default</button>` : ''}
            </div>
          </div>
        </div>`;
    }).join('');
  } catch(e) { toast(e.message,'error'); }
}

function toggleAccordion(id) {
  document.getElementById(id).classList.toggle('open');
}

async function editPromptFor(sid) {
  _currentPromptSid = sid;
  document.getElementById('prompt-modal-sid').textContent = sid;
  try {
    const ss = await GET('/section-systems');
    document.getElementById('prompt-modal-text').value = ss[sid] || '';
  } catch(e) { document.getElementById('prompt-modal-text').value = ''; }
  openModal('prompt-modal');
}

async function savePrompt() {
  const text = document.getElementById('prompt-modal-text').value.trim();
  if (!text) { toast('Prompt cannot be empty','error'); return; }
  try {
    await PUT(`/section-systems/${_currentPromptSid}`, { system_prompt: text });
    toast('Prompt saved','success');
    closeModal('prompt-modal');
    if (document.getElementById('page-section-prompts').classList.contains('active')) loadSectionPrompts();
  } catch(e) { toast(e.message,'error'); }
}

async function resetPrompt() {
  confirmAction('Reset Prompt', `Reset the system prompt for "${_currentPromptSid}" to its source default?`, async () => {
    try {
      await DELETE(`/section-systems/${_currentPromptSid}`);
      toast('Prompt reset','success');
      closeModal('prompt-modal');
      if (document.getElementById('page-section-prompts').classList.contains('active')) loadSectionPrompts();
    } catch(e) { toast(e.message,'error'); }
  });
}

async function resetSectionPrompt(sid) {
  confirmAction('Reset Prompt', `Reset "${sid}" prompt to default?`, async () => {
    try {
      await DELETE(`/section-systems/${sid}`);
      toast('Prompt reset','success');
      loadSectionPrompts();
    } catch(e) { toast(e.message,'error'); }
  });
}


// ══════════════════════════════════════════════════════════════════════════════
// COMPLIANCE RULES
// ══════════════════════════════════════════════════════════════════════════════
async function initComplianceRules() {
  try {
    const cr  = await GET('/compliance-rules');
    const sel = document.getElementById('cr-doctype-select');
    const cur = sel.value;
    sel.innerHTML = Object.keys(cr).map(dt => `<option value="${dt}">${dt}</option>`).join('');
    if (cur && cr[cur]) sel.value = cur;
    loadComplianceRules();
  } catch(e) { toast(e.message,'error'); }
}

async function loadComplianceRules() {
  const dt = document.getElementById('cr-doctype-select').value;
  if (!dt) return;
  try {
    const data = await GET(`/compliance-rules/${encodeURIComponent(dt)}`);
    const rules = data.rules || [];
    document.getElementById('cr-rule-count').textContent = `${rules.length} rules`;
    const tbody = document.getElementById('cr-rules-table');
    tbody.innerHTML = rules.length ? rules.map(r => `
      <tr>
        <td><code>${r.id}</code></td>
        <td><span class="badge badge-${r.severity}">${r.severity}</span></td>
        <td><code style="font-size:10px;word-break:break-all">${escHtml(r.pattern || '')}</code></td>
        <td style="max-width:200px">${escHtml(r.desc || '')}</td>
        <td style="max-width:180px;color:var(--muted)">${escHtml(r.fix || '')}</td>
        <td><code style="font-size:10px">${r.ref || ''}</code></td>
        <td>
          <div class="flex-row">
            <button class="btn btn-ghost" style="padding:4px 8px;font-size:11px" onclick="openEditRuleModal('${dt}',${JSON.stringify(r).replace(/"/g,"&quot;")})">✏</button>
            <button class="btn btn-danger" style="padding:4px 8px;font-size:11px" onclick="deleteRule('${dt}','${r.id}')">🗑</button>
          </div>
        </td>
      </tr>`).join('') : '<tr><td colspan="7" class="empty">No rules defined</td></tr>';
  } catch(e) { toast(e.message,'error'); }
}

function openAddRuleModal() {
  _currentRuleEditId = null;
  document.getElementById('rule-modal-title').textContent = 'Add Compliance Rule';
  document.getElementById('rule-modal-ok').textContent    = 'Add Rule';
  ['rule-id','rule-pattern','rule-desc','rule-fix','rule-ref'].forEach(id => document.getElementById(id).value='');
  document.getElementById('rule-severity').value = 'warning';
  document.getElementById('rule-required').checked = true;
  openModal('rule-modal');
}

function openEditRuleModal(dt, rule) {
  _currentRuleEditId = rule.id;
  document.getElementById('rule-modal-title').textContent = 'Edit Compliance Rule';
  document.getElementById('rule-modal-ok').textContent    = 'Save Rule';
  document.getElementById('rule-id').value       = rule.id;
  document.getElementById('rule-id').disabled    = true;
  document.getElementById('rule-pattern').value  = rule.pattern || '';
  document.getElementById('rule-desc').value     = rule.desc    || '';
  document.getElementById('rule-fix').value      = rule.fix     || '';
  document.getElementById('rule-ref').value      = rule.ref     || '';
  document.getElementById('rule-severity').value = rule.severity || 'warning';
  document.getElementById('rule-required').checked = !!rule.required;
  openModal('rule-modal');
}

async function saveRule() {
  const dt = document.getElementById('cr-doctype-select').value;
  const rule = {
    id:       document.getElementById('rule-id').value.trim(),
    pattern:  document.getElementById('rule-pattern').value.trim(),
    severity: document.getElementById('rule-severity').value,
    desc:     document.getElementById('rule-desc').value.trim(),
    fix:      document.getElementById('rule-fix').value.trim(),
    ref:      document.getElementById('rule-ref').value.trim(),
    required: document.getElementById('rule-required').checked,
  };
  if (!rule.id || !rule.pattern || !rule.desc || !rule.fix) {
    toast('ID, Pattern, Description, and Fix are required','error'); return;
  }
  try {
    if (_currentRuleEditId) {
      await PUT(`/compliance-rules/${encodeURIComponent(dt)}/${rule.id}`, rule);
      toast('Rule updated','success');
    } else {
      await POST(`/compliance-rules/${encodeURIComponent(dt)}`, rule);
      toast('Rule added','success');
    }
    document.getElementById('rule-id').disabled = false;
    closeModal('rule-modal');
    loadComplianceRules();
  } catch(e) { toast(e.message,'error'); }
}

async function deleteRule(dt, ruleId) {
  confirmAction('Delete Rule', `Remove rule "${ruleId}" from "${dt}"?`, async () => {
    try {
      await DELETE(`/compliance-rules/${encodeURIComponent(dt)}/${ruleId}`);
      toast('Rule deleted','success');
      loadComplianceRules();
    } catch(e) { toast(e.message,'error'); }
  });
}


// ══════════════════════════════════════════════════════════════════════════════
// REGULATORY GUIDELINES
// ══════════════════════════════════════════════════════════════════════════════
async function initGuidelines() {
  try {
    const data = await GET('/guidelines');
    const regs = data.regulatory || {};
    const sel  = document.getElementById('gl-doctype-select');
    const cur  = sel.value;
    sel.innerHTML = Object.keys(regs).map(dt => `<option value="${dt}">${dt}</option>`).join('');
    if (cur && regs[cur]) sel.value = cur;
    loadGuidelines();
  } catch(e) { toast(e.message,'error'); }
}

async function loadGuidelines() {
  const dt = document.getElementById('gl-doctype-select').value;
  if (!dt) return;
  try {
    const data = await GET('/guidelines');
    const regs = (data.regulatory || {})[dt] || {};
    const container = document.getElementById('gl-list');
    container.innerHTML = Object.entries(regs).length ? Object.entries(regs).map(([name, text]) => `
      <div class="accordion" id="gl-acc-${name.replace(/[^a-z0-9]/gi,'_')}">
        <div class="accordion-header" onclick="toggleAccordion('gl-acc-${name.replace(/[^a-z0-9]/gi,'_')}')">
          📜 ${escHtml(name)}
          <span class="accordion-chevron">▼</span>
        </div>
        <div class="accordion-body">
          <textarea id="gl-edit-${name.replace(/[^a-z0-9]/gi,'_')}" style="min-height:120px;margin-bottom:8px">${escHtml(text)}</textarea>
          <div class="flex-row">
            <button class="btn btn-primary" onclick="saveGuidelineEdit('${escHtml(dt)}','${escHtml(name)}','${name.replace(/[^a-z0-9]/gi,'_')}')">💾 Save</button>
            <button class="btn btn-danger" onclick="deleteGuidelineEntry('${escHtml(dt)}','${escHtml(name)}')">🗑 Delete</button>
          </div>
        </div>
      </div>`).join('') : '<div class="empty"><div class="empty-icon">📜</div>No guidelines for this document type</div>';
  } catch(e) { toast(e.message,'error'); }
}

async function saveGuidelineEdit(dt, name, safeId) {
  const text = document.getElementById(`gl-edit-${safeId}`).value.trim();
  if (!text) { toast('Content required','error'); return; }
  try {
    await PUT(`/guidelines/${encodeURIComponent(dt)}/${encodeURIComponent(name)}`, { text });
    toast('Guideline saved','success');
  } catch(e) { toast(e.message,'error'); }
}

async function deleteGuidelineEntry(dt, name) {
  confirmAction('Delete Guideline', `Remove "${name}" from "${dt}" guidelines?`, async () => {
    try {
      await DELETE(`/guidelines/${encodeURIComponent(dt)}/${encodeURIComponent(name)}`);
      toast('Guideline deleted','success');
      loadGuidelines();
    } catch(e) { toast(e.message,'error'); }
  });
}

function openAddGuidelineModal() {
  document.getElementById('gl-name-input').value = '';
  document.getElementById('gl-text-input').value = '';
  openModal('guideline-modal');
}

async function saveGuideline() {
  const dt   = document.getElementById('gl-doctype-select').value;
  const name = document.getElementById('gl-name-input').value.trim();
  const text = document.getElementById('gl-text-input').value.trim();
  if (!name || !text) { toast('Name and content required','error'); return; }
  try {
    await PUT(`/guidelines/${encodeURIComponent(dt)}/${encodeURIComponent(name)}`, { text });
    toast('Guideline added','success');
    closeModal('guideline-modal');
    loadGuidelines();
  } catch(e) { toast(e.message,'error'); }
}


// ══════════════════════════════════════════════════════════════════════════════
// PHASE GUIDELINES
// ══════════════════════════════════════════════════════════════════════════════
async function loadPhaseGuidelines() {
  try {
    const data  = await GET('/guidelines');
    const phase = data.phase || {};
    const container = document.getElementById('pg-list');
    container.innerHTML = Object.entries(phase).length ? Object.entries(phase).map(([key, text]) => `
      <div class="accordion" id="pg-acc-${key.replace(/[^a-z0-9]/gi,'_')}">
        <div class="accordion-header" onclick="toggleAccordion('pg-acc-${key.replace(/[^a-z0-9]/gi,'_')}')">
          🔬 ${escHtml(key)}
          <span class="accordion-chevron">▼</span>
        </div>
        <div class="accordion-body">
          <textarea id="pg-edit-${key.replace(/[^a-z0-9]/gi,'_')}" style="min-height:120px;margin-bottom:8px">${escHtml(text)}</textarea>
          <div class="flex-row">
            <button class="btn btn-primary" onclick="savePhaseEdit('${escHtml(key)}','${key.replace(/[^a-z0-9]/gi,'_')}')">💾 Save</button>
          </div>
        </div>
      </div>`).join('') : '<div class="empty"><div class="empty-icon">🔬</div>No phase guidelines</div>';
  } catch(e) { toast(e.message,'error'); }
}

async function savePhaseEdit(key, safeId) {
  const text = document.getElementById(`pg-edit-${safeId}`).value.trim();
  if (!text) { toast('Content required','error'); return; }
  try {
    await PUT(`/guidelines/phase/${encodeURIComponent(key)}`, { text });
    toast('Saved','success');
  } catch(e) { toast(e.message,'error'); }
}

function openAddPhaseModal() {
  _currentPhaseKey = null;
  document.getElementById('phase-modal-title').textContent = 'Add Phase Guideline';
  document.getElementById('phase-modal-ok').textContent    = 'Add';
  document.getElementById('pg-key-input').value  = '';
  document.getElementById('pg-text-input').value = '';
  openModal('phase-modal');
}

async function savePhaseGuideline() {
  const key  = document.getElementById('pg-key-input').value.trim();
  const text = document.getElementById('pg-text-input').value.trim();
  if (!key || !text) { toast('Phase key and content required','error'); return; }
  try {
    await POST('/guidelines/phase', { phase_key: key, text });
    toast('Phase guideline added','success');
    closeModal('phase-modal');
    loadPhaseGuidelines();
  } catch(e) { toast(e.message,'error'); }
}


// ══════════════════════════════════════════════════════════════════════════════
// RESET / EXPORT
// ══════════════════════════════════════════════════════════════════════════════
async function resetKey(key) {
  confirmAction('Reset ' + key, `Restore "${key}" to source defaults? Your edits for this key will be lost.`, async () => {
    try {
      await POST('/reset', { key });
      toast(`"${key}" reset to defaults`, 'success');
    } catch(e) { toast(e.message,'error'); }
  });
}

async function resetAll() {
  confirmAction('Reset ALL Overrides', 'This will delete your entire admin_overrides.json file and restore ALL defaults. This cannot be undone.', async () => {
    try {
      await POST('/reset', {});
      toast('All overrides cleared','success');
    } catch(e) { toast(e.message,'error'); }
  });
}

async function exportOverrides() {
  try {
    const [sm, ss, cr, gl, pg] = await Promise.all([
      GET('/section-map'), GET('/section-systems'),
      GET('/compliance-rules'), GET('/guidelines'),
      GET('/guidelines'),
    ]);
    const blob = new Blob([JSON.stringify({
      section_map: sm, section_systems: ss,
      compliance_rules: cr, regulatory_guidelines: gl.regulatory,
      phase_guidelines: gl.phase,
      _exported_at: new Date().toISOString(),
    }, null, 2)], { type: 'application/json' });
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = 'admin_overrides.json';
    a.click();
    toast('Exported','success');
  } catch(e) { toast(e.message,'error'); }
}


// ══════════════════════════════════════════════════════════════════════════════
// API EXPLORER
// ══════════════════════════════════════════════════════════════════════════════
const API_ENDPOINTS = [
  { method:'GET',    path:'/overview',                     desc:'System overview and stats' },
  { method:'GET',    path:'/section-map',                  desc:'All document type section maps' },
  { method:'GET',    path:'/section-map/{doc_type}',       desc:'Sections for one document type' },
  { method:'PUT',    path:'/section-map/{doc_type}',       desc:'Replace all sections for a doc type' },
  { method:'POST',   path:'/section-map/{doc_type}/sections', desc:'Add one section' },
  { method:'DELETE', path:'/section-map/{doc_type}/sections/{sid}', desc:'Remove one section' },
  { method:'GET',    path:'/section-systems',              desc:'All AI system prompts' },
  { method:'PUT',    path:'/section-systems/{section_id}', desc:'Update one system prompt' },
  { method:'DELETE', path:'/section-systems/{section_id}', desc:'Reset to default' },
  { method:'GET',    path:'/compliance-rules',             desc:'All compliance rules' },
  { method:'GET',    path:'/compliance-rules/{doc_type}',  desc:'Rules for one doc type' },
  { method:'POST',   path:'/compliance-rules/{doc_type}',  desc:'Add a rule' },
  { method:'PUT',    path:'/compliance-rules/{doc_type}/{rule_id}', desc:'Update a rule' },
  { method:'DELETE', path:'/compliance-rules/{doc_type}/{rule_id}', desc:'Delete a rule' },
  { method:'GET',    path:'/guidelines',                   desc:'All regulatory + phase guidelines' },
  { method:'PUT',    path:'/guidelines/{doc_type}/{name}', desc:'Add or update a guideline' },
  { method:'DELETE', path:'/guidelines/{doc_type}/{name}', desc:'Delete an override guideline' },
  { method:'PUT',    path:'/guidelines/phase/{phase_key}', desc:'Update phase guideline' },
  { method:'POST',   path:'/guidelines/phase',             desc:'Add new phase guideline' },
  { method:'POST',   path:'/reset',                        desc:'Reset overrides (all or by key)' },
];

const METHOD_COLORS = { GET:'#00C48C', POST:'#20BEFF', PUT:'#FFB020', DELETE:'#FF5C5C' };

function renderApiExplorer() {
  const container = document.getElementById('api-list');
  container.innerHTML = API_ENDPOINTS.map((ep,i) => `
    <div class="accordion" id="api-acc-${i}">
      <div class="accordion-header" onclick="toggleAccordion('api-acc-${i}')">
        <span style="font-family:monospace;font-size:11px;padding:2px 7px;border-radius:4px;background:${METHOD_COLORS[ep.method]}22;color:${METHOD_COLORS[ep.method]};font-weight:700;min-width:55px;text-align:center">${ep.method}</span>
        <code style="color:var(--text2)">/admin${ep.path}</code>
        <span style="color:var(--muted);font-size:12px;margin-left:8px">${ep.desc}</span>
        <span class="accordion-chevron">▼</span>
      </div>
      <div class="accordion-body">
        <div class="flex-row" style="margin-bottom:8px;flex-wrap:wrap;gap:6px">
          <code style="flex:1;padding:6px 10px;border-radius:6px;background:var(--overlay)">
            ${ep.method} http://localhost:8765/admin${ep.path}
          </code>
          <button class="btn btn-ghost" style="font-size:11px;padding:4px 10px" onclick="copyText('${ep.method} http://localhost:8765/admin${ep.path}')">📋 Copy</button>
          <a href="/docs#/admin${ep.path.replace(/\//g,'')+ep.method.toLowerCase()}" target="_blank" class="btn btn-ghost" style="font-size:11px;padding:4px 10px">📖 Swagger</a>
        </div>
      </div>
    </div>`).join('');
}

function copyText(txt) {
  navigator.clipboard.writeText(txt).then(() => toast('Copied!','info',1500));
}


// ══════════════════════════════════════════════════════════════════════════════
// UTILITIES
// ══════════════════════════════════════════════════════════════════════════════
function escHtml(str) {
  return String(str || '').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}

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

// ── Init ─────────────────────────────────────────────────────────────────────
applyThemeName(getSavedThemeName());
loadDashboard();
</script>
</body>
</html>"""
