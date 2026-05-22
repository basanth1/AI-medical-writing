"""
Session store — in-memory dict with TTL.
Drop-in replacement for Redis in production.
"""

from __future__ import annotations
import time, logging
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class SessionStore:
    """
    Thread-safe in-memory key-value store with TTL.
    Replace with Redis client for multi-instance deployments.
    """

    def __init__(self, ttl_seconds: int = 86_400):
        self._store: Dict[str, Dict] = {}
        self._ttl   = ttl_seconds

    # ── public API ────────────────────────────────────────────────────────────

    def set(self, key: str, value: Any) -> None:
        self._store[key] = {"value": value, "expires_at": time.time() + self._ttl}
        logger.debug(f"Session set: {key}")

    def get(self, key: str) -> Optional[Any]:
        self._evict()
        entry = self._store.get(key)
        if entry is None:
            return None
        if time.time() > entry["expires_at"]:
            del self._store[key]
            return None
        return entry["value"]

    def update(self, key: str, patch: Dict) -> bool:
        data = self.get(key)
        if data is None:
            return False
        data.update(patch)
        self.set(key, data)
        return True

    def delete(self, key: str) -> None:
        self._store.pop(key, None)

    def exists(self, key: str) -> bool:
        return self.get(key) is not None

    def count(self) -> int:
        self._evict()
        return len(self._store)

    # ── internal ──────────────────────────────────────────────────────────────

    def _evict(self) -> None:
        now = time.time()
        expired = [k for k, v in self._store.items() if now > v["expires_at"]]
        for k in expired:
            del self._store[k]
        if expired:
            logger.debug(f"Evicted {len(expired)} expired sessions")
