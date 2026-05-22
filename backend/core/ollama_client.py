"""
backend/core/ollama_client.py
Ollama Client — PRIMARY text generation using gpt-oss:120b.

Implements the exact streaming pattern from the specification:

    client = Client(
        host='https://ollama.com',
        headers={'Authorization': 'Bearer ' + os.environ.get('OLLAMA_API_KEY')}
    )
    messages = [{'role': 'user', 'content': prompt, 'system': system}]
    section = ""
    for part in client.chat('gpt-oss:120b', messages=messages, stream=True):
        section += part.message.content
    return section

No per-token cost. GroqClient is used only for validation and as fallback.
"""

import os
import logging
import time
from typing import Generator, List, Optional

logger = logging.getLogger(__name__)

# Silence noisy httpx INFO logs
logging.getLogger("httpx").setLevel(logging.WARNING)

try:
    from ollama import Client as _OllamaSDK
    _OLLAMA_SDK_AVAILABLE = True
except ImportError:
    _OLLAMA_SDK_AVAILABLE = False
    logger.warning("ollama SDK not installed — run: pip install ollama")

from backend.data.models_config import (
    OLLAMA_MODEL,
    OLLAMA_HOST,
    OLLAMA_TIMEOUT,
    DEFAULT_SYSTEM_PROMPT,
)


class OllamaClient:
    """
    Primary LLM client using gpt-oss:120b via the Ollama streaming API.

    All document section generation goes through here first.
    GroqClient is only called when this client fails or is unavailable.
    """

    def __init__(
        self,
        api_key:  Optional[str] = None,
        model:    Optional[str] = None,          # None → use OLLAMA_MODEL from config
        host:     Optional[str] = None,          # None → use OLLAMA_HOST from config
        timeout:  int           = OLLAMA_TIMEOUT,
    ):
        self._api_key = api_key  or os.environ.get("OLLAMA_API_KEY", "")
        self.model    = model    or os.environ.get("OLLAMA_MODEL", OLLAMA_MODEL)
        self.host     = host     or os.environ.get("OLLAMA_HOST",  OLLAMA_HOST)
        self.timeout  = timeout
        self._client: Optional[_OllamaSDK] = None
        self._init()

    # ── Initialisation ────────────────────────────────────────────────────────

    def _init(self) -> None:
        if not _OLLAMA_SDK_AVAILABLE:
            logger.warning("OllamaClient: `pip install ollama` to enable primary generation")
            return
        if not self._api_key:
            logger.warning("OLLAMA_API_KEY not set — OllamaClient unavailable")
            return
        try:
            self._client = _OllamaSDK(
                host=self.host,
                headers={"Authorization": f"Bearer {self._api_key}"},
            )
            logger.info(
                f"OllamaClient ready — model: {self.model}  host: {self.host}"
            )
        except Exception as exc:
            logger.error(f"OllamaClient init failed: {exc}")

    # ── Message builder ───────────────────────────────────────────────────────

    @staticmethod
    def _build_messages(prompt: str, system: str) -> List[dict]:
        """
        Build messages in the exact format from the specification.
        System instruction is embedded in the user message dict
        (Ollama non-standard field — keeps the spec pattern intact).
        """
        return [
            {
                "role":    "user",
                "content": prompt,
                "system":  system,
            }
        ]

    # ── Public interface ──────────────────────────────────────────────────────

    def chat(self, prompt: str, *, system: str = DEFAULT_SYSTEM_PROMPT) -> str:
        """
        Generate text using streaming — accumulates all chunks into one string.

        Exactly matches the spec pattern:
            section = ""
            for part in client.chat('gpt-oss:120b', messages=messages, stream=True):
                section += part.message.content
            return section
        """
        if not self._client:
            raise RuntimeError(
                "OllamaClient not initialised — check OLLAMA_API_KEY "
                "and `pip install ollama`"
            )

        messages = self._build_messages(prompt, system)
        section  = ""
        t0       = time.monotonic()

        for part in self._client.chat(
            self.model,
            messages=messages,
            stream=True,
        ):
            content = part.message.content
            if content:
                section += content

        elapsed = time.monotonic() - t0
        words   = len(section.split())
        logger.debug(
            f"Ollama [{self.model}] streamed {words} words in {elapsed:.1f}s"
        )
        return section.strip()

    def chat_with_system(self, system: str, prompt: str) -> str:
        """Explicit system + user order — preferred for section generation."""
        return self.chat(prompt, system=system)

    def stream(
        self, prompt: str, *, system: str = DEFAULT_SYSTEM_PROMPT
    ) -> Generator[str, None, None]:
        """Yield text chunks as they arrive — for SSE / real-time display."""
        if not self._client:
            raise RuntimeError("OllamaClient not initialised")

        messages = self._build_messages(prompt, system)
        for part in self._client.chat(
            self.model, messages=messages, stream=True
        ):
            content = part.message.content
            if content:
                yield content

    def is_available(self) -> bool:
        return self._client is not None

    def ping(self) -> bool:
        """Quick connectivity check."""
        if not self._client:
            return False
        try:
            self._client.list()
            return True
        except Exception:
            return False

    def switch_model(self, model: str) -> None:
        """Hot-swap model at runtime — no restart needed."""
        self.model = model
        logger.info(f"OllamaClient: switched to model '{model}'")

    def __call__(self, prompt: str, **kwargs) -> str:
        return self.chat(prompt, **kwargs)

    def __repr__(self) -> str:
        status = "connected" if self._client else "unavailable"
        return (
            f"<OllamaClient "
            f"model={self.model} "
            f"host={self.host} "
            f"status={status}>"
        )
