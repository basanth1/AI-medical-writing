// // frontend/src/data/theme.js
// // Light/dark mode theme definitions and Zustand slice.
// // All CSS variables are defined here and applied to :root via ThemeProvider.

// export const THEMES = {
//   dark: {
//     name: 'dark',
//     label: 'Dark',

//     // Backgrounds
//     '--bg-base':       '#0d0f14',
//     '--bg-surface':    '#131720',
//     '--bg-elevated':   '#1a2030',
//     '--bg-overlay':    '#212840',
//     '--bg-hover':      '#1e2535',

//     // Borders
//     '--border-subtle': 'rgba(255,255,255,0.06)',
//     '--border-soft':   'rgba(255,255,255,0.10)',
//     '--border-mid':    'rgba(255,255,255,0.16)',

//     // Brand accent — amber/gold
//     '--accent':        '#e8a94a',
//     '--accent-dim':    '#b07830',
//     '--accent-glow':   'rgba(232,169,74,0.15)',
//     '--accent-text':   '#f5c878',

//     // Semantic
//     '--success':     '#34c97b',
//     '--success-dim': 'rgba(52,201,123,0.12)',
//     '--warning':     '#f5a623',
//     '--warning-dim': 'rgba(245,166,35,0.12)',
//     '--danger':      '#f04444',
//     '--danger-dim':  'rgba(240,68,68,0.12)',
//     '--info':        '#4a9eff',
//     '--info-dim':    'rgba(74,158,255,0.12)',

//     // Text
//     '--text-primary':   '#f0f2f7',
//     '--text-secondary': '#8892a4',
//     '--text-muted':     '#50596a',
//     '--text-accent':    '#f5c878',

//     // Background radial hints
//     '--bg-radial-1': 'rgba(232,169,74,0.04)',
//     '--bg-radial-2': 'rgba(74,158,255,0.03)',
//   },

//   light: {
//     name: 'light',
//     label: 'Light',

//     // Backgrounds
//     '--bg-base':       '#f4f5f8',
//     '--bg-surface':    '#ffffff',
//     '--bg-elevated':   '#f0f2f7',
//     '--bg-overlay':    '#e8eaf0',
//     '--bg-hover':      '#ebedf5',

//     // Borders
//     '--border-subtle': 'rgba(0,0,0,0.06)',
//     '--border-soft':   'rgba(0,0,0,0.10)',
//     '--border-mid':    'rgba(0,0,0,0.16)',

//     // Brand accent — deeper amber for light bg
//     '--accent':        '#c47c1a',
//     '--accent-dim':    '#9a5e0e',
//     '--accent-glow':   'rgba(196,124,26,0.12)',
//     '--accent-text':   '#8a5010',

//     // Semantic
//     '--success':     '#1a7a48',
//     '--success-dim': 'rgba(26,122,72,0.10)',
//     '--warning':     '#a06010',
//     '--warning-dim': 'rgba(160,96,16,0.10)',
//     '--danger':      '#c02020',
//     '--danger-dim':  'rgba(192,32,32,0.10)',
//     '--info':        '#1a60c0',
//     '--info-dim':    'rgba(26,96,192,0.10)',

//     // Text
//     '--text-primary':   '#111827',
//     '--text-secondary': '#4b5563',
//     '--text-muted':     '#9ca3af',
//     '--text-accent':    '#8a5010',

//     // Background radial hints
//     '--bg-radial-1': 'rgba(196,124,26,0.05)',
//     '--bg-radial-2': 'rgba(26,96,192,0.04)',
//   },
// }

// // ── Fixed tokens (same in both themes) ───────────────────────────────────────
// export const FIXED_TOKENS = {
//   '--radius-sm': '6px',
//   '--radius-md': '10px',
//   '--radius-lg': '14px',
//   '--radius-xl': '20px',
//   '--font-display': "'DM Serif Display', Georgia, serif",
//   '--font-body':    "'DM Sans', system-ui, sans-serif",
//   '--font-mono':    "'JetBrains Mono', 'Fira Code', monospace",
// }

// /** Apply a theme object to document.documentElement */
// export function applyTheme(theme) {
//   const root = document.documentElement
//   const tokens = { ...FIXED_TOKENS, ...theme }
//   Object.entries(tokens).forEach(([key, val]) => {
//     if (key.startsWith('--') || key === 'name' || key === 'label') {
//       if (key !== 'name' && key !== 'label') root.style.setProperty(key, val)
//     }
//   })
//   root.setAttribute('data-theme', theme.name)
// }

// /** Read saved theme from localStorage, default to dark */
// export function getSavedTheme() {
//   try {
//     const saved = localStorage.getItem('ctdgen-theme')
//     return THEMES[saved] || THEMES.dark
//   } catch {
//     return THEMES.dark
//   }
// }

// export function saveTheme(themeName) {
//   try { localStorage.setItem('ctdgen-theme', themeName) } catch {}
// }
// src/data/theme.js
// Kaggle-inspired design tokens — crisp, professional, data-science aesthetic.
// Dark: deep navy/slate base with electric blue accents.
// Light: pure white base with the same blue accent family.

export const THEMES = {
  dark: {
    name: 'dark',
    vars: {
      // ── Backgrounds ──────────────────────────────────────────────────────
      '--bg-base':     '#0B0F19',   // deepest navy — page background
      '--bg-surface':  '#111827',   // card/panel surface
      '--bg-elevated': '#1A2236',   // elevated elements, inputs
      '--bg-overlay':  '#1E2A40',   // hover overlays, code blocks
      '--bg-hover':    '#243048',   // subtle hover state

      // ── Borders ───────────────────────────────────────────────────────────
      '--border-subtle': '#1E2A40', // barely-there dividers
      '--border-soft':   '#263347', // card borders, input borders
      '--border-mid':    '#2E3E56', // stronger borders

      // ── Text ─────────────────────────────────────────────────────────────
      '--text-primary':   '#F0F4FF', // near-white, high contrast
      '--text-secondary': '#A8B4CC', // labels, subtitles
      '--text-muted':     '#5C6E8A', // placeholders, captions
      '--text-inverse':   '#0B0F19', // text on coloured buttons

      // ── Accent — Kaggle electric blue ────────────────────────────────────
      '--accent':       '#20BEFF',   // primary CTAs, links, active states
      '--accent-text':  '#20BEFF',
      '--accent-dim':   '#20BEFF33',
      '--accent-glow':  '#20BEFF14',

      // ── Semantic colours ──────────────────────────────────────────────────
      '--success':     '#00C48C',
      '--success-dim': '#00C48C18',
      '--warning':     '#FFB020',
      '--warning-dim': '#FFB02018',
      '--danger':      '#FF5C5C',
      '--danger-dim':  '#FF5C5C18',
      '--info':        '#20BEFF',
      '--info-dim':    '#20BEFF18',

      // ── Typography ────────────────────────────────────────────────────────
      '--font-body':    "'Inter', 'Segoe UI', system-ui, sans-serif",
      '--font-display': "'Inter', 'Segoe UI', system-ui, sans-serif",
      '--font-mono':    "'JetBrains Mono', 'Fira Code', 'Consolas', monospace",

      // ── Radii ─────────────────────────────────────────────────────────────
      '--radius-sm': '6px',
      '--radius-md': '8px',
      '--radius-lg': '12px',
      '--radius-xl': '16px',
    },
  },

  light: {
    name: 'light',
    vars: {
      // ── Backgrounds ───────────────────────────────────────────────────────
     '--bg-base':     '#EAF7FF',
'--bg-surface':  '#F8FCFF',
'--bg-elevated': '#DDF1FC',
'--bg-overlay':  '#CBE7F7',
'--bg-hover':    '#B6DFF3',
      // ── Borders ───────────────────────────────────────────────────────────
      '--border-subtle': '#E8EEF6',
      '--border-soft':   '#D1DCF0',
      '--border-mid':    '#B8CADE',

      // ── Text ──────────────────────────────────────────────────────────────
      '--text-primary':   '#0D1B2E',
      '--text-secondary': '#3A5068',
      '--text-muted':     '#7A90A8',
      '--text-inverse':   '#FFFFFF',

      // ── Accent ────────────────────────────────────────────────────────────
      '--accent':       '#0099D8',   // slightly deeper blue for light readability
      '--accent-text':  '#0099D8',
      '--accent-dim':   '#0099D833',
      '--accent-glow':  '#0099D810',

      // ── Semantic ──────────────────────────────────────────────────────────
      '--success':     '#00A572',
      '--success-dim': '#00A57215',
      '--warning':     '#D97706',
      '--warning-dim': '#D9770615',
      '--danger':      '#DC2626',
      '--danger-dim':  '#DC262615',
      '--info':        '#0099D8',
      '--info-dim':    '#0099D815',

      // ── Typography ────────────────────────────────────────────────────────
      '--font-body':    "'Inter', 'Segoe UI', system-ui, sans-serif",
      '--font-display': "'Inter', 'Segoe UI', system-ui, sans-serif",
      '--font-mono':    "'JetBrains Mono', 'Fira Code', 'Consolas', monospace",

      // ── Radii ─────────────────────────────────────────────────────────────
      '--radius-sm': '6px',
      '--radius-md': '8px',
      '--radius-lg': '12px',
      '--radius-xl': '16px',
    },
  },
}

export function applyTheme(theme) {
  const root = document.documentElement
  Object.entries(theme.vars).forEach(([k, v]) => root.style.setProperty(k, v))
  root.setAttribute('data-theme', theme.name)
  document.body.style.background = theme.vars['--bg-base']
}

export function getSavedTheme() {
  const saved = localStorage.getItem('ctdgen-theme')
  return saved === 'light' ? THEMES.light : THEMES.dark
}

export function saveTheme(name) {
  localStorage.setItem('ctdgen-theme', name)
}