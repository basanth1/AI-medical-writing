"""
backend/data — all static configuration, rules, templates, and knowledge base.
Import from here rather than hardcoding data in service files.
"""
from .models_config import (
    GROQ_MODELS,
    GROQ_RATE_INTERVAL,
    OLLAMA_MODEL,
    OLLAMA_HOST,
    OLLAMA_TIMEOUT,
    DEFAULT_SYSTEM_PROMPT,
)
from .regulatory_guidelines import REGULATORY_GUIDELINES, PHASE_GUIDELINES, get_guidelines
from .sample_documents      import SAMPLE_DOCUMENTS
from .compliance_rules      import (
    COMPLIANCE_RULES,
    REQUIRED_SECTION_IDS,
    GUIDELINES_PER_TYPE,
    ENTITY_PATTERNS,
)
from .section_templates     import SECTION_MAP, SECTION_SYSTEMS, DEFAULT_SECTION_SYSTEM

__all__ = [
    # models_config
    "GROQ_MODELS", "GROQ_RATE_INTERVAL",
    "OLLAMA_MODEL", "OLLAMA_HOST", "OLLAMA_TIMEOUT",
    "DEFAULT_SYSTEM_PROMPT",
    # regulatory_guidelines
    "REGULATORY_GUIDELINES", "PHASE_GUIDELINES", "get_guidelines",
    # sample_documents
    "SAMPLE_DOCUMENTS",
    # compliance_rules
    "COMPLIANCE_RULES", "REQUIRED_SECTION_IDS", "GUIDELINES_PER_TYPE", "ENTITY_PATTERNS",
    # section_templates
    "SECTION_MAP", "SECTION_SYSTEMS", "DEFAULT_SECTION_SYSTEM",
]
