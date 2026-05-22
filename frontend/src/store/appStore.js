import { create } from 'zustand'
import { THEMES, applyTheme, getSavedTheme, saveTheme } from '../data/theme.js'

export const useAppStore = create((set, get) => ({
  // ── Server ────────────────────────────────────────────────────────────────
  serverStatus:    'idle',
  ollamaAvailable: false,
  ollamaModel:     '',
  groqAvailable:   false,
  groqFallbackModel:  '',
  activeGenerator: 'template',
  vectorStats:     null,
  setServerStatus:    (s) => set({ serverStatus: s }),
  setOllamaAvailable: (v) => set({ ollamaAvailable: v }),
  setOllamaModel:     (m) => set({ ollamaModel: m }),
  setGroqAvailable:   (v) => set({ groqAvailable: v }),
  setGroqFallbackModel: (m) => set({ groqFallbackModel: m }),
  setActiveGenerator: (g) => set({ activeGenerator: g }),
  setVectorStats:     (s) => set({ vectorStats: s }),

  // ── Generation ────────────────────────────────────────────────────────────
  currentStep:      0,
  generationStage:  -1,
  sessionId:        null,
  documentType:     'Clinical Study Protocol',
  generationResult: null,
  isGenerating:     false,
  
  setStep:             (s) => set({ currentStep: s }),
  setGenerationStage:  (s) => set({ generationStage: s }),
  setSessionId:        (id) => set({ sessionId: id }),
  setDocumentType:     (t) => set({ documentType: t }),
  setGenerationResult: (r) => set({ generationResult: r }),
  setIsGenerating:     (v) => set({ isGenerating: v }),

  // ── Active section ────────────────────────────────────────────────────────
  sections: [],
  activeSectionIdx:    0,
  setSections: (sections) => set({ sections }),
  setActiveSectionIdx: (i) => set({ activeSectionIdx: i }),

  // ── Feedback ──────────────────────────────────────────────────────────────
  feedbackLog: [],
  addFeedback:   (fb) => set((s) => ({ feedbackLog: [...s.feedbackLog, fb] })),
  clearFeedback: ()   => set({ feedbackLog: [] }),
  complianceReport: null,
  setComplianceReport: (r) => set({ complianceReport: r }),
  // ── Theme ─────────────────────────────────────────────────────────────────
  theme: getSavedTheme(),

  toggleTheme: () => {
    const current = get().theme
    const next = current.name === 'dark' ? THEMES.light : THEMES.dark
    applyTheme(next)
    saveTheme(next.name)
    set({ theme: next })
  },

  initTheme: () => {
    const t = getSavedTheme()
    applyTheme(t)
    set({ theme: t })
  },

  // ── User preferences ──────────────────────────────────────────────────────
  userPrefs: {
    name:         '',
    role:         'Medical Writer',
    organization: '',
    autoCompliance: true,
    compactView:  false,
  },
  setUserPrefs: (prefs) => set((s) => ({ userPrefs: { ...s.userPrefs, ...prefs } })),

  // ── Reset ─────────────────────────────────────────────────────────────────
  resetSession: () => set({
    currentStep: 0, generationStage: -1, sessionId: null,
    generationResult: null, isGenerating: false,
    activeSectionIdx: 0, feedbackLog: [],sections: [],
    complianceReport: null,
  }),
  finalizedDocs:    [],
setFinalizedDocs: (docs) => set({ finalizedDocs: docs }),
addFinalizedDoc:  (doc)  => set(s => ({
  finalizedDocs: [doc, ...s.finalizedDocs.filter(d => d.session_id !== doc.session_id)],
})),
}))
