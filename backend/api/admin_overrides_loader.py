"""
backend/api/admin_overrides_loader.py
Patches the data module globals at startup so admin edits
(stored in backend/db/admin_overrides.json) take effect in
generation_service, compliance_service, and rag_service
without restarting the server.

Call apply_overrides() once at app startup from app.py.
After that, any PUT/POST/DELETE to the admin endpoints automatically
re-applies overrides by calling apply_overrides() internally.

Usage in app.py:
    from backend.api.admin_overrides_loader import apply_overrides
    apply_overrides()   # call once before uvicorn.run()
"""
from __future__ import annotations
import json
import os
import logging

logger = logging.getLogger(__name__)

_OVERRIDE_FILE = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "db", "admin_overrides.json")
)


def _load() -> dict:
    if not os.path.isfile(_OVERRIDE_FILE):
        return {}
    try:
        with open(_OVERRIDE_FILE, encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"admin_overrides.json load failed: {e}")
        return {}


def apply_overrides() -> None:
    """
    Merge admin_overrides.json on top of the default module globals.
    Safe to call multiple times — always re-reads the file.
    """
    overrides = _load()
    if not overrides:
        logger.info("admin_overrides: no overrides file found — using source defaults")
        return

    applied = []

    # ── 1. SECTION_MAP ────────────────────────────────────────────────────────
    if "section_map" in overrides:
        try:
            import backend.data.section_templates as st
            sm_override = overrides["section_map"]
            # Merge: override keys win, missing keys keep source defaults
            for doc_type, sections in sm_override.items():
                # Convert [[sid, title], ...] → list of tuples for SECTION_MAP
                st.SECTION_MAP[doc_type] = [tuple(s) for s in sections]
            applied.append("section_map")
        except Exception as e:
            logger.error(f"apply_overrides section_map failed: {e}")

    # ── 2. SECTION_SYSTEMS ────────────────────────────────────────────────────
    if "section_systems" in overrides:
        try:
            import backend.data.section_templates as st
            for sid, prompt in overrides["section_systems"].items():
                st.SECTION_SYSTEMS[sid] = prompt
            applied.append("section_systems")
        except Exception as e:
            logger.error(f"apply_overrides section_systems failed: {e}")

    # ── 3. COMPLIANCE_RULES ───────────────────────────────────────────────────
    if "compliance_rules" in overrides:
        try:
            import backend.data.compliance_rules as cr
            for doc_type, rules in overrides["compliance_rules"].items():
                cr.COMPLIANCE_RULES[doc_type] = rules
            applied.append("compliance_rules")
        except Exception as e:
            logger.error(f"apply_overrides compliance_rules failed: {e}")

    # ── 4. REGULATORY_GUIDELINES ──────────────────────────────────────────────
    if "regulatory_guidelines" in overrides:
        try:
            import backend.data.regulatory_guidelines as rg
            for doc_type, guidelines in overrides["regulatory_guidelines"].items():
                if doc_type not in rg.REGULATORY_GUIDELINES:
                    rg.REGULATORY_GUIDELINES[doc_type] = {}
                rg.REGULATORY_GUIDELINES[doc_type].update(guidelines)
            applied.append("regulatory_guidelines")
        except Exception as e:
            logger.error(f"apply_overrides regulatory_guidelines failed: {e}")

    # ── 5. PHASE_GUIDELINES ───────────────────────────────────────────────────
    if "phase_guidelines" in overrides:
        try:
            import backend.data.regulatory_guidelines as rg
            rg.PHASE_GUIDELINES.update(overrides["phase_guidelines"])
            applied.append("phase_guidelines")
        except Exception as e:
            logger.error(f"apply_overrides phase_guidelines failed: {e}")

    if applied:
        logger.info(f"admin_overrides applied: {applied}")
    else:
        logger.info("admin_overrides: file exists but no recognised keys found")


def apply_and_reload(key: str | None = None) -> None:
    """
    Called by admin REST endpoints after a write so changes take effect
    immediately without restarting the server.
    `key` is for logging only — always re-applies all overrides.
    """
    apply_overrides()
    if key:
        logger.info(f"admin_overrides reloaded after change to '{key}'")
