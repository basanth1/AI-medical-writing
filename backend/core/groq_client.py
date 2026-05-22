"""
backend/core/groq_client.py
Groq Client — VALIDATOR and FALLBACK only.

Roles:
  1. Validator  — llama-3.1-8b-instant    (fast, cheap, checks Ollama output)
  2. Fallback   — llama-3.3-70b-versatile (full generation when Ollama fails)

Never import this directly from services.
Use LLMClient — it decides which backend to call.
"""

import os, logging, time, random
from typing import Generator, List, Optional

logger = logging.getLogger(__name__)

# Silence noisy httpx / groq retry INFO lines (429 retries are handled internally)
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("groq._base_client").setLevel(logging.WARNING)
logging.getLogger("groq").setLevel(logging.WARNING)

try:
    from groq import Groq, RateLimitError
    _GROQ_SDK = True
except ImportError:
    _GROQ_SDK = False
    logger.warning("groq SDK not installed — run: pip install groq")

from backend.data.models_config import (
    GROQ_MODELS,
    GROQ_RATE_INTERVAL,
    DEFAULT_SYSTEM_PROMPT,
)


class _RateLimiter:
    """Token-bucket with jitter — prevents 429s on Groq free tier."""
    def __init__(self, interval: float = 2.5):
        self.interval  = interval
        self._last: float = 0.0

    def wait(self) -> None:
        elapsed = time.monotonic() - self._last
        if elapsed < self.interval:
            time.sleep(self.interval - elapsed + random.uniform(0.05, 0.3))
        self._last = time.monotonic()


class GroqClient:
    """
    Groq validator + fallback.

    validation_chat()
        Uses llama-3.1-8b-instant — short prompt, fast response, very cheap.
        Called after Ollama generates a section to verify quality.

    chat() / chat_with_system()
        Uses llama-3.3-70b-versatile — full generation quality.
        Called only when OllamaClient is unavailable or fails.
    """

    def __init__(
        self,
        api_key:     Optional[str] = None,
        model:       str           = "medical",   # default for fallback generation
        temperature: float         = 0.2,
        max_tokens:  int           = 2048,
    ):
        self._key        = api_key or os.environ.get("GROQ_API_KEY", "")
        self.model_name  = GROQ_MODELS.get(model, GROQ_MODELS["medical"])
        self.temperature = temperature
        self.max_tokens  = max_tokens
        self._client: Optional[Groq] = None
        self._limiter    = _RateLimiter(GROQ_RATE_INTERVAL.get(model, 2.5))
        self._init()

    def _init(self) -> None:
        if not _GROQ_SDK:
            return
        if self._key:
            self._client = Groq(api_key=self._key)
            logger.info(
                f"GroqClient ready — "
                f"validator: {GROQ_MODELS['validator']}  "
                f"fallback: {self.model_name}"
            )
        else:
            logger.warning("GROQ_API_KEY not set — GroqClient unavailable (validator + fallback disabled)")

    def _msgs(self, prompt: str, system: str) -> List[dict]:
        return [
            {"role": "system", "content": system},
            {"role": "user",   "content": prompt},
        ]

    def _call(self, fn, max_retries: int = 4) -> str:
        """Exponential backoff on 429 RateLimitError."""
        for attempt in range(max_retries):
            try:
                self._limiter.wait()
                return fn()
            except Exception as exc:
                # Detect rate limit by type name (avoids conditional import dance)
                is_rate_limit = type(exc).__name__ == "RateLimitError"
                if attempt >= max_retries - 1:
                    raise
                wait = (
                    (2 ** (attempt + 2)) + random.uniform(0.5, 1.5)
                    if is_rate_limit
                    else 1.5 * (attempt + 1)
                )
                logger.debug(
                    f"Groq {'429' if is_rate_limit else 'error'} — "
                    f"retry {attempt+1}/{max_retries} in {wait:.1f}s"
                )
                time.sleep(wait)
        raise RuntimeError("Unreachable")

    # ── Public interface ──────────────────────────────────────────────────────

    def validation_chat(
        self,
        prompt: str,
        *,
        system: str = DEFAULT_SYSTEM_PROMPT,
    ) -> str:
        """
        Fast validation call using llama-3.1-8b-instant.
        Used to check Ollama output for compliance issues.
        Small token budget — just needs to identify issues, not write content.
        """
        if not self._client:
            return ""
        validator_model = GROQ_MODELS["validator"]   # llama-3.1-8b-instant
        return self._call(lambda: self._client.chat.completions.create(
            model       = validator_model,
            messages    = self._msgs(prompt, system),
            temperature = 0.1,     # near-deterministic — reproducible validation
            max_tokens  = 512,     # validation summaries are short
        ).choices[0].message.content.strip())

    def chat(self, prompt: str, *, system: str = DEFAULT_SYSTEM_PROMPT) -> str:
        """
        Full fallback generation using llama-3.3-70b-versatile.
        Only called when OllamaClient is unavailable.
        """
        if not self._client:
            return self._template_fallback(prompt)
        return self._call(lambda: self._client.chat.completions.create(
            model       = self.model_name,    # llama-3.3-70b-versatile
            messages    = self._msgs(prompt, system),
            temperature = self.temperature,
            max_tokens  = self.max_tokens,
        ).choices[0].message.content.strip())

    def chat_with_system(self, system: str, prompt: str) -> str:
        return self.chat(prompt, system=system)

    def stream(
        self, prompt: str, *, system: str = DEFAULT_SYSTEM_PROMPT
    ) -> Generator[str, None, None]:
        if not self._client:
            yield self._template_fallback(prompt)
            return
        self._limiter.wait()
        for chunk in self._client.chat.completions.create(
            model       = self.model_name,
            messages    = self._msgs(prompt, system),
            temperature = self.temperature,
            max_tokens  = self.max_tokens,
            stream      = True,
        ):
            delta = chunk.choices[0].delta.content
            if delta:
                yield delta

    def is_available(self) -> bool:
        return self._client is not None

    def _template_fallback(self, prompt: str) -> str:
        indication = next(
            (kw for kw in [
                "Oncology", "Cardiology", "Neurology",
                "Endocrinology", "Immunology", "Hematology",
            ] if kw.lower() in prompt.lower()),
            "the studied indication",
        )
        return (
            f"[TEMPLATE — set OLLAMA_API_KEY for gpt-oss:120b generation "
            f"or GROQ_API_KEY for llama-3.3-70b fallback]\n\n"
            f"This section covers {indication}-specific clinical trial requirements:\n"
            "1. Scientific rationale and unmet medical need\n"
            "2. Study design justification per ICH E8\n"
            "3. Endpoint selection rationale\n"
            "4. Patient population eligibility criteria\n"
            "5. Risk-benefit assessment per ICH E6\n"
        )

    def __call__(self, prompt: str, **kwargs) -> str:
        return self.chat(prompt, **kwargs)

    def __repr__(self) -> str:
        status = "connected" if self._client else "unavailable"
        return (
            f"<GroqClient "
            f"validator={GROQ_MODELS['validator']} "
            f"fallback={self.model_name} "
            f"status={status}>"
        )

    # ── Convenience helpers (used by tests and batch workflows) ───────────────

    def batch(
        self,
        prompts: List[str],
        *,
        system: str = DEFAULT_SYSTEM_PROMPT,
        delay:  float = 0.0,
    ) -> List[str]:
        """Sequential batch with optional extra spacing between calls."""
        import time as _time
        results = []
        for i, p in enumerate(prompts):
            results.append(self.chat(p, system=system))
            if delay > 0 and i < len(prompts) - 1:
                _time.sleep(delay)
        return results

    def count_tokens(self, text: str) -> int:
        """Rough token estimate (4 chars ≈ 1 token)."""
        return len(text) // 4
