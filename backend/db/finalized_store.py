"""
backend/db/finalized_store.py

Persists finalized documents to disk so they survive server restarts.

Storage layout:
    backend/db/finalized_documents/
    └── <session_id>.json   ← full snapshot: metadata, sections, feedback, compliance
"""

from __future__ import annotations

import json
import os
import logging
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)

_STORE_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "finalized_documents")
)


class FinalizedDocumentStore:
    """
    Simple disk-backed store for finalized clinical trial documents.
    Each document is saved as a single JSON file keyed by session_id.
    Thread-safe for read-heavy workloads (single write per finalization).
    """

    def __init__(self, store_dir: str = _STORE_DIR):
        self._dir = store_dir
        os.makedirs(self._dir, exist_ok=True)
        logger.info(f"FinalizedDocumentStore ready at: {self._dir}")

    # ── Public API ─────────────────────────────────────────────────────────────

    def save(self, session_id: str, record: Dict) -> None:
        """
        Persist a finalized document record to disk.
        Overwrites any existing file for the same session_id.
        """
        path = self._path(session_id)
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(record, f, ensure_ascii=False, indent=2)
            logger.info(f"[finalized] Saved: {session_id}")
        except Exception as exc:
            logger.error(f"[finalized] Failed to save {session_id}: {exc}")
            raise

    def get(self, session_id: str) -> Optional[Dict]:
        """Return a single finalized document or None if not found."""
        path = self._path(session_id)
        if not os.path.exists(path):
            return None
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as exc:
            logger.error(f"[finalized] Failed to read {session_id}: {exc}")
            return None

    def list_all(self) -> List[Dict]:
        """
        Return all finalized documents sorted newest-first.
        Only the summary fields are returned (no full section content) to keep
        the list response lightweight; use get() for full detail.
        """
        records = []
        for fname in os.listdir(self._dir):
            if not fname.endswith(".json"):
                continue
            session_id = fname[:-5]
            doc = self.get(session_id)
            if doc:
                records.append({
                    "session_id":       doc.get("session_id"),
                    "document_type":    doc.get("document_type"),
                    "document_name":    doc.get("document_name", doc.get("document_type", "Untitled")),
                    "indication":       doc.get("metadata", {}).get("indication", ""),
                    "phase":            doc.get("metadata", {}).get("phase", ""),
                    "finalized_at":     doc.get("finalized_at", ""),
                    "compliance_score": doc.get("compliance_score", 0),
                    "section_count":    len(doc.get("sections", [])),
                    "feedback_count":   len(doc.get("feedback_log", [])),
                    "total_words":      sum(s.get("word_count", 0) for s in doc.get("sections", [])),
                })
        records.sort(key=lambda r: r.get("finalized_at", ""), reverse=True)
        return records

    def delete(self, session_id: str) -> bool:
        """Delete a finalized document. Returns True if deleted, False if not found."""
        path = self._path(session_id)
        if not os.path.exists(path):
            return False
        os.remove(path)
        logger.info(f"[finalized] Deleted: {session_id}")
        return True

    def exists(self, session_id: str) -> bool:
        return os.path.exists(self._path(session_id))

    # ── Internal ───────────────────────────────────────────────────────────────

    def _path(self, session_id: str) -> str:
        # Sanitize to prevent path traversal
        safe = session_id.replace("/", "_").replace("..", "_")
        return os.path.join(self._dir, f"{safe}.json")
