"""
backend/api/admin_routes.py
Admin REST API — CRUD endpoints for section maps, compliance rules,
regulatory guidelines, and LLM system prompts.

All data is persisted to backend/db/admin_overrides.json so edits
survive server restarts without touching the source Python files.
At startup the overrides file is merged on top of the defaults.
"""
from __future__ import annotations

import json
import os
import re
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, Body
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from pydantic import BaseModel

logger = logging.getLogger(__name__)

admin_router = APIRouter(prefix="/admin", tags=["admin"])

# ── Overrides persistence path ────────────────────────────────────────────────
_OVERRIDE_FILE = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "db", "admin_overrides.json")
)
os.makedirs(os.path.dirname(_OVERRIDE_FILE), exist_ok=True)


def _load_overrides() -> dict:
    if os.path.isfile(_OVERRIDE_FILE):
        try:
            with open(_OVERRIDE_FILE, encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load admin overrides: {e}")
    return {}


def _save_overrides(data: dict) -> None:
    data["_updated_at"] = datetime.now(timezone.utc).isoformat()
    with open(_OVERRIDE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def _get_override(key: str, default: Any) -> Any:
    return _load_overrides().get(key, default)


def _set_override(key: str, value: Any) -> None:
    overrides = _load_overrides()
    overrides[key] = value
    _save_overrides(overrides)
    # Re-apply immediately so changes take effect without a server restart
    try:
        from backend.api.admin_overrides_loader import apply_and_reload
        apply_and_reload(key)
    except Exception as e:
        logger.warning(f"Live reload failed (restart to apply): {e}")


# ── Lazy imports from data modules (avoids circular imports) ──────────────────
def _get_defaults():
    from backend.data.section_templates  import SECTION_MAP, SECTION_SYSTEMS, DEFAULT_SECTION_SYSTEM
    from backend.data.compliance_rules   import COMPLIANCE_RULES, REQUIRED_SECTION_IDS
    from backend.data.regulatory_guidelines import REGULATORY_GUIDELINES, PHASE_GUIDELINES
    return {
        "section_map":            SECTION_MAP,
        "section_systems":        SECTION_SYSTEMS,
        "default_section_system": DEFAULT_SECTION_SYSTEM,
        "compliance_rules":       COMPLIANCE_RULES,
        "required_section_ids":   REQUIRED_SECTION_IDS,
        "regulatory_guidelines":  REGULATORY_GUIDELINES,
        "phase_guidelines":       PHASE_GUIDELINES,
    }


# ── Helper: merge overrides onto defaults ─────────────────────────────────────
def get_effective_section_map() -> dict:
    defaults  = _get_defaults()["section_map"]
    overrides = _get_override("section_map", {})
    return {**defaults, **overrides}

def get_effective_section_systems() -> dict:
    defaults  = _get_defaults()["section_systems"]
    overrides = _get_override("section_systems", {})
    return {**defaults, **overrides}

def get_effective_compliance_rules() -> dict:
    defaults  = _get_defaults()["compliance_rules"]
    overrides = _get_override("compliance_rules", {})
    return {**defaults, **overrides}

def get_effective_guidelines() -> dict:
    defaults  = _get_defaults()["regulatory_guidelines"]
    overrides = _get_override("regulatory_guidelines", {})
    return {**defaults, **overrides}

def get_effective_phase_guidelines() -> dict:
    defaults  = _get_defaults()["phase_guidelines"]
    overrides = _get_override("phase_guidelines", {})
    return {**defaults, **overrides}


# ═════════════════════════════════════════════════════════════════════════════
# REST ENDPOINTS
# ═════════════════════════════════════════════════════════════════════════════

# ── Overview ──────────────────────────────────────────────────────────────────
@admin_router.get("/overview")
def overview():
    defs = _get_defaults()
    eff_sm  = get_effective_section_map()
    eff_cr  = get_effective_compliance_rules()
    eff_gl  = get_effective_guidelines()
    return {
        "document_types":         list(eff_sm.keys()),
        "total_sections":         sum(len(v) for v in eff_sm.values()),
        "section_system_overrides": len(_get_override("section_systems", {})),
        "compliance_rule_counts": {k: len(v) for k, v in eff_cr.items()},
        "guidelines_loaded":      {k: list(v.keys()) for k, v in eff_gl.items()},
        "phase_guidelines":       list(get_effective_phase_guidelines().keys()),
        "overrides_file":         _OVERRIDE_FILE,
        "has_overrides":          os.path.isfile(_OVERRIDE_FILE),
    }


# ─────────────────────────────────────────────────────────────────────────────
# SECTION MAP
# ─────────────────────────────────────────────────────────────────────────────

@admin_router.get("/section-map")
def get_section_map():
    return get_effective_section_map()

@admin_router.get("/section-map/{doc_type}")
def get_section_map_for_type(doc_type: str):
    sm = get_effective_section_map()
    if doc_type not in sm:
        raise HTTPException(404, f"Document type '{doc_type}' not found")
    return {"doc_type": doc_type, "sections": sm[doc_type]}

@admin_router.put("/section-map/{doc_type}")
def update_section_map(doc_type: str, sections: List[List[str]] = Body(...)):
    """
    Replace all sections for a document type.
    Body: [[section_id, display_title], ...]
    """
    for item in sections:
        if not isinstance(item, list) or len(item) != 2:
            raise HTTPException(400, "Each section must be [section_id, display_title]")

    overrides = _get_override("section_map", {})
    overrides[doc_type] = sections
    _set_override("section_map", overrides)
    return {"ok": True, "doc_type": doc_type, "sections": sections}

@admin_router.post("/section-map/{doc_type}/sections")
def add_section(doc_type: str, section: List[str] = Body(...)):
    """Add one section: [section_id, display_title]"""
    if len(section) != 2:
        raise HTTPException(400, "Provide [section_id, display_title]")
    eff = get_effective_section_map()
    current = list(eff.get(doc_type, []))
    if any(s[0] == section[0] for s in current):
        raise HTTPException(409, f"Section '{section[0]}' already exists in '{doc_type}'")
    current.append(section)
    overrides = _get_override("section_map", {})
    overrides[doc_type] = current
    _set_override("section_map", overrides)
    return {"ok": True, "sections": current}

@admin_router.delete("/section-map/{doc_type}/sections/{section_id}")
def delete_section(doc_type: str, section_id: str):
    eff     = get_effective_section_map()
    current = list(eff.get(doc_type, []))
    new     = [s for s in current if s[0] != section_id]
    if len(new) == len(current):
        raise HTTPException(404, f"Section '{section_id}' not found in '{doc_type}'")
    overrides = _get_override("section_map", {})
    overrides[doc_type] = new
    _set_override("section_map", overrides)
    return {"ok": True, "removed": section_id, "remaining": new}

@admin_router.post("/section-map/document-types")
def add_document_type(body: dict = Body(...)):
    """Create a new document type with an initial empty section list."""
    doc_type = body.get("doc_type", "").strip()
    if not doc_type:
        raise HTTPException(400, "doc_type is required")
    eff = get_effective_section_map()
    if doc_type in eff:
        raise HTTPException(409, f"Document type '{doc_type}' already exists")
    overrides = _get_override("section_map", {})
    overrides[doc_type] = []
    _set_override("section_map", overrides)
    return {"ok": True, "doc_type": doc_type}

@admin_router.delete("/section-map/document-types/{doc_type}")
def delete_document_type(doc_type: str):
    overrides = _get_override("section_map", {})
    if doc_type not in overrides:
        raise HTTPException(400, "Can only delete custom document types (not built-in defaults)")
    del overrides[doc_type]
    _set_override("section_map", overrides)
    return {"ok": True, "deleted": doc_type}


# ─────────────────────────────────────────────────────────────────────────────
# SECTION SYSTEM PROMPTS
# ─────────────────────────────────────────────────────────────────────────────

@admin_router.get("/section-systems")
def get_section_systems():
    return get_effective_section_systems()

@admin_router.get("/section-systems/{section_id}")
def get_section_system(section_id: str):
    ss = get_effective_section_systems()
    if section_id not in ss:
        raise HTTPException(404, f"No system prompt for section '{section_id}'")
    return {"section_id": section_id, "system_prompt": ss[section_id]}

@admin_router.put("/section-systems/{section_id}")
def update_section_system(section_id: str, body: dict = Body(...)):
    """Update the LLM system prompt for a section."""
    prompt = body.get("system_prompt", "").strip()
    if not prompt:
        raise HTTPException(400, "system_prompt is required")
    overrides = _get_override("section_systems", {})
    overrides[section_id] = prompt
    _set_override("section_systems", overrides)
    return {"ok": True, "section_id": section_id}

@admin_router.delete("/section-systems/{section_id}")
def reset_section_system(section_id: str):
    """Reset a section system prompt to its default."""
    overrides = _get_override("section_systems", {})
    removed = overrides.pop(section_id, None)
    _set_override("section_systems", overrides)
    return {"ok": True, "reset": section_id, "was_overridden": removed is not None}


# ─────────────────────────────────────────────────────────────────────────────
# COMPLIANCE RULES
# ─────────────────────────────────────────────────────────────────────────────

@admin_router.get("/compliance-rules")
def get_compliance_rules():
    return get_effective_compliance_rules()

@admin_router.get("/compliance-rules/{doc_type}")
def get_compliance_rules_for_type(doc_type: str):
    cr = get_effective_compliance_rules()
    if doc_type not in cr:
        raise HTTPException(404, f"No rules for document type '{doc_type}'")
    return {"doc_type": doc_type, "rules": cr[doc_type]}

@admin_router.post("/compliance-rules/{doc_type}")
def add_compliance_rule(doc_type: str, rule: dict = Body(...)):
    """
    Add a new compliance rule.
    Required fields: id, pattern, severity (critical|warning|info), desc, fix
    Optional: required (bool), ref (str)
    """
    required_fields = {"id", "pattern", "severity", "desc", "fix"}
    missing = required_fields - set(rule.keys())
    if missing:
        raise HTTPException(400, f"Missing fields: {missing}")
    if rule["severity"] not in ("critical", "warning", "info"):
        raise HTTPException(400, "severity must be critical, warning, or info")
    try:
        re.compile(rule["pattern"])
    except re.error as e:
        raise HTTPException(400, f"Invalid regex pattern: {e}")

    overrides = _get_override("compliance_rules", {})
    current   = list(get_effective_compliance_rules().get(doc_type, []))
    if any(r["id"] == rule["id"] for r in current):
        raise HTTPException(409, f"Rule '{rule['id']}' already exists")
    rule.setdefault("required", True)
    rule.setdefault("ref", "")
    current.append(rule)
    overrides[doc_type] = current
    _set_override("compliance_rules", overrides)
    return {"ok": True, "rule_id": rule["id"]}

@admin_router.put("/compliance-rules/{doc_type}/{rule_id}")
def update_compliance_rule(doc_type: str, rule_id: str, updates: dict = Body(...)):
    """Update one or more fields of an existing rule."""
    if "pattern" in updates:
        try:
            re.compile(updates["pattern"])
        except re.error as e:
            raise HTTPException(400, f"Invalid regex pattern: {e}")

    overrides = _get_override("compliance_rules", {})
    current   = list(get_effective_compliance_rules().get(doc_type, []))
    found     = False
    for r in current:
        if r["id"] == rule_id:
            r.update(updates)
            found = True
            break
    if not found:
        raise HTTPException(404, f"Rule '{rule_id}' not found in '{doc_type}'")
    overrides[doc_type] = current
    _set_override("compliance_rules", overrides)
    return {"ok": True, "rule_id": rule_id}

@admin_router.delete("/compliance-rules/{doc_type}/{rule_id}")
def delete_compliance_rule(doc_type: str, rule_id: str):
    overrides = _get_override("compliance_rules", {})
    current   = list(get_effective_compliance_rules().get(doc_type, []))
    new       = [r for r in current if r["id"] != rule_id]
    if len(new) == len(current):
        raise HTTPException(404, f"Rule '{rule_id}' not found")
    overrides[doc_type] = new
    _set_override("compliance_rules", overrides)
    return {"ok": True, "removed": rule_id}


# ─────────────────────────────────────────────────────────────────────────────
# REGULATORY GUIDELINES
# ─────────────────────────────────────────────────────────────────────────────

@admin_router.get("/guidelines")
def get_all_guidelines():
    return {
        "regulatory": get_effective_guidelines(),
        "phase":      get_effective_phase_guidelines(),
    }

@admin_router.put("/guidelines/{doc_type}/{guideline_name}")
def update_guideline(doc_type: str, guideline_name: str, body: dict = Body(...)):
    text = body.get("text", "").strip()
    if not text:
        raise HTTPException(400, "text is required")
    overrides = _get_override("regulatory_guidelines", {})
    overrides.setdefault(doc_type, {})
    overrides[doc_type][guideline_name] = text
    _set_override("regulatory_guidelines", overrides)
    return {"ok": True, "doc_type": doc_type, "guideline": guideline_name}

@admin_router.delete("/guidelines/{doc_type}/{guideline_name}")
def delete_guideline(doc_type: str, guideline_name: str):
    overrides = _get_override("regulatory_guidelines", {})
    if doc_type not in overrides or guideline_name not in overrides.get(doc_type, {}):
        raise HTTPException(404, "Guideline override not found (cannot delete built-in defaults)")
    del overrides[doc_type][guideline_name]
    _set_override("regulatory_guidelines", overrides)
    return {"ok": True, "deleted": guideline_name}

@admin_router.put("/guidelines/phase/{phase_key}")
def update_phase_guideline(phase_key: str, body: dict = Body(...)):
    text = body.get("text", "").strip()
    if not text:
        raise HTTPException(400, "text is required")
    overrides = _get_override("phase_guidelines", {})
    overrides[phase_key] = text
    _set_override("phase_guidelines", overrides)
    return {"ok": True, "phase": phase_key}

@admin_router.post("/guidelines/phase")
def add_phase_guideline(body: dict = Body(...)):
    phase_key = body.get("phase_key", "").strip()
    text      = body.get("text", "").strip()
    if not phase_key or not text:
        raise HTTPException(400, "phase_key and text are required")
    overrides = _get_override("phase_guidelines", {})
    overrides[phase_key] = text
    _set_override("phase_guidelines", overrides)
    return {"ok": True, "phase": phase_key}


# ─────────────────────────────────────────────────────────────────────────────
# RESET
# ─────────────────────────────────────────────────────────────────────────────

@admin_router.post("/reset")
def reset_all(body: dict = Body(default={})):
    """Reset ALL overrides (or a specific key) back to source defaults."""
    key = body.get("key")
    if key:
        overrides = _load_overrides()
        removed = overrides.pop(key, None)
        _save_overrides(overrides)
        return {"ok": True, "reset_key": key, "was_present": removed is not None}
    if os.path.isfile(_OVERRIDE_FILE):
        os.remove(_OVERRIDE_FILE)
    return {"ok": True, "message": "All overrides cleared — using source defaults"}


# ─────────────────────────────────────────────────────────────────────────────
# ADMIN UI — served at GET /admin/ui
# ─────────────────────────────────────────────────────────────────────────────

@admin_router.get("/logo.png", include_in_schema=False)
def admin_logo():
    """Serve the admin sidebar logo from the backend package."""
    logo_path = os.path.join(os.path.dirname(__file__), "new circulants logo.png")
    if not os.path.isfile(logo_path):
        raise HTTPException(404, "Admin logo not found")
    return FileResponse(logo_path, media_type="image/png")


@admin_router.get("/favicon.png", include_in_schema=False)
def admin_favicon():
    """Serve the square admin favicon."""
    favicon_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "..", "frontend", "public", "circulants-favicon.png")
    )
    if not os.path.isfile(favicon_path):
        raise HTTPException(404, "Admin favicon not found")
    return FileResponse(favicon_path, media_type="image/png")


@admin_router.get("/ui", response_class=HTMLResponse, include_in_schema=False)
def admin_ui():
    """Serve the interactive admin dashboard."""
    from backend.api.admin_ui_html import ADMIN_UI_HTML
    return HTMLResponse(content=ADMIN_UI_HTML)
