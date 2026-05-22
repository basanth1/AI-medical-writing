"""
backend/data/models_config.py
LLM model definitions — single source of truth for all model names.

To change any model: edit here only. No other file needs updating.
"""

# ── Ollama — PRIMARY text generation (free, no per-token cost) ────────────────
#
#   Model   : gpt-oss:120b
#   Source  : confirmed by user
#   Host    : https://ollama.com  (override with OLLAMA_HOST env var)
#
OLLAMA_MODEL:   str = "gpt-oss:120b"
OLLAMA_HOST:    str = "https://ollama.com"
OLLAMA_TIMEOUT: int = 180          # seconds — 120B model needs extra time to stream

# ── Groq — VALIDATOR + FALLBACK (paid, fast, reliable) ────────────────────────
#
#   Validator model : llama-3.1-8b-instant
#     • Used for: post-generation compliance validation checks
#     • Why 8B: fast (~1s), cheap, sufficient for structured issue-detection
#
#   Fallback model  : llama-3.3-70b-versatile
#     • Used for: full section generation when Ollama is unreachable
#     • Same quality level as previous default
#
GROQ_MODELS: dict[str, str] = {
    "fast":      "llama-3.1-8b-instant",      # validator — cheap, quick
    "default":   "llama-3.3-70b-versatile",   # confirmed by user
    "medical":   "llama-3.3-70b-versatile",   # confirmed by user
    "validator": "llama-3.1-8b-instant",      # explicit alias for validation calls
}

# Groq free-tier rate-limit spacing (seconds between requests)
GROQ_RATE_INTERVAL: dict[str, float] = {
    "fast":      1.5,   # 8B: ~30 req/min — 1.5s keeps well within limit
    "default":   2.5,   # 70B: ~30 req/min — 2.5s for safe margin
    "medical":   2.5,
    "validator": 1.5,
}

# ── Shared default system prompt ──────────────────────────────────────────────
DEFAULT_SYSTEM_PROMPT = (
    "You are an expert medical writer specializing in clinical trial documentation. "
    "You produce precise, regulatory-compliant documents following ICH E6, ICH E3, "
    "FDA, and EMA guidelines. Your writing is formal, accurate, complete, and uses "
    "standard clinical trial terminology. Never use placeholders unless instructed."
)
