// import { Sun, Moon } from 'lucide-react'
// import { useAppStore } from '../../store/appStore.js'

// export default function ThemeToggle({ size = 16 }) {
//   const { theme, toggleTheme } = useAppStore()
//   const isDark = theme.name === 'dark'

//   return (
//     <button
//       className="theme-toggle"
//       onClick={toggleTheme}
//       title={isDark ? 'Switch to light mode' : 'Switch to dark mode'}
//       aria-label={isDark ? 'Switch to light mode' : 'Switch to dark mode'}
//     >
//       {isDark
//         ? <Sun  size={size} />
//         : <Moon size={size} />}
//     </button>
//   )
// }
import { Sun, Moon } from 'lucide-react'
import { useAppStore } from '../../store/appStore.js'

export default function ThemeToggle({ size = 16 }) {
  const { theme, toggleTheme } = useAppStore()
  const isDark = theme.name === 'dark'

  return (
    <button
      onClick={toggleTheme}
      title={isDark ? 'Switch to light mode' : 'Switch to dark mode'}
      aria-label={isDark ? 'Switch to light mode' : 'Switch to dark mode'}
      style={{
        display:        'inline-flex',
        alignItems:     'center',
        justifyContent: 'center',
        width:          34,
        height:         34,
        borderRadius:   'var(--radius-md)',
        border:         '1px solid var(--border-soft)',
        background:     'var(--bg-elevated)',
        color:          isDark ? '#FFB020' : '#0099D8',
        cursor:         'pointer',
        transition:     'background 0.15s, border-color 0.15s, color 0.15s, transform 0.15s',
        flexShrink:     0,
      }}
      onMouseEnter={e => {
        e.currentTarget.style.background   = 'var(--bg-overlay)'
        e.currentTarget.style.borderColor  = 'var(--border-mid)'
        e.currentTarget.style.transform    = 'scale(1.08)'
      }}
      onMouseLeave={e => {
        e.currentTarget.style.background   = 'var(--bg-elevated)'
        e.currentTarget.style.borderColor  = 'var(--border-soft)'
        e.currentTarget.style.transform    = 'scale(1)'
      }}
    >
      {isDark
        ? <Sun  size={size} strokeWidth={1.8} />
        : <Moon size={size} strokeWidth={1.8} />
      }
    </button>
  )
}