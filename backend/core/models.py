"""
Data models — single source of truth for all request/response schemas.
"""
from __future__ import annotations
from pydantic import BaseModel, ConfigDict, Field, field_validator
from typing import Optional, List, Dict, Any
from enum import Enum
from datetime import datetime, timezone
import re


def _utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


# ── Enumerations ──────────────────────────────────────────────────────────────

class DocumentType(str, Enum):
    CSP = "Clinical Study Protocol"
    ICF = "Informed Consent Form"
    CSR = "Clinical Study Report"
    SAP = "Statistical Analysis Plan"
    IB  = "Investigator Brochure"

class StudyPhase(str, Enum):
    PHASE_1  = "Phase I"
    PHASE_1B = "Phase Ib"
    PHASE_2  = "Phase II"
    PHASE_2B = "Phase IIb"
    PHASE_3  = "Phase III"
    PHASE_4  = "Phase IV"

class StudyDesign(str, Enum):
    RCT        = "Randomized, Controlled, Double-blind"
    OPEN_LABEL = "Randomized, Open-label"
    SINGLE_ARM = "Single-arm, Open-label"
    CROSSOVER  = "Crossover"
    ADAPTIVE   = "Adaptive Design"
    OBS        = "Observational"

class FeedbackAction(str, Enum):
    APPROVE = "approve"
    REVISE  = "revise"
    REJECT  = "reject"

class IssueSeverity(str, Enum):
    CRITICAL = "critical"
    WARNING  = "warning"
    INFO     = "info"


# ── Core domain models ────────────────────────────────────────────────────────

class StudyMetadata(BaseModel):
    indication:              str           = Field(..., description="Medical indication")
    phase:                   str           = Field(..., description="Phase I/II/III/IV")
    design:                  str           = Field(..., description="Study design")
    primary_endpoint:        str           = Field(..., description="Primary efficacy endpoint")
    secondary_endpoints:     List[str]     = Field(default_factory=list)
    patient_population:      str           = Field(..., description="Target population")
    sample_size:             Optional[int] = None
    duration_months:         Optional[int] = None
    treatment_arms:          List[str]     = Field(default_factory=list)
    investigational_product: Optional[str] = None
    sponsor:                 Optional[str] = None
    therapeutic_area:        Optional[str] = None
    country:                 str           = "Multi-national"
    protocol_number:         Optional[str] = None

    @field_validator("phase")
    @classmethod
    def validate_phase(cls, v: str) -> str:
        if not any(p in v for p in ["Phase", "I", "II", "III", "IV"]):
            raise ValueError("phase must contain a Roman numeral (I–IV)")
        return v

    def to_query_text(self) -> str:
        parts = [
            f"Indication: {self.indication}",
            f"Phase: {self.phase}",
            f"Design: {self.design}",
            f"Primary Endpoint: {self.primary_endpoint}",
            f"Population: {self.patient_population}",
        ]
        if self.secondary_endpoints:
            parts.append(f"Secondary Endpoints: {', '.join(self.secondary_endpoints)}")
        if self.investigational_product:
            parts.append(f"Drug: {self.investigational_product}")
        if self.therapeutic_area:
            parts.append(f"Therapeutic Area: {self.therapeutic_area}")
        return " | ".join(parts)

    def to_prompt_context(self) -> str:
        lines = [
            "=== STUDY METADATA ===",
            f"Indication           : {self.indication}",
            f"Therapeutic Area     : {self.therapeutic_area or self.indication}",
            f"Phase                : {self.phase}",
            f"Design               : {self.design}",
            f"Primary Endpoint     : {self.primary_endpoint}",
        ]
        if self.secondary_endpoints:
            lines.append(f"Secondary Endpoints  : {'; '.join(self.secondary_endpoints)}")
        lines += [
            f"Patient Population   : {self.patient_population}",
            f"Sample Size          : {self.sample_size or 'TBD'}",
            f"Study Duration       : {self.duration_months or 'TBD'} months",
            f"Investigational Drug : {self.investigational_product or '[INVESTIGATIONAL_PRODUCT]'}",
            f"Sponsor              : {self.sponsor or '[SPONSOR_NAME]'}",
            f"Protocol Number      : {self.protocol_number or '[PROTOCOL_NUMBER]'}",
        ]
        if self.treatment_arms:
            lines.append(f"Treatment Arms       : {'; '.join(self.treatment_arms)}")
        return "\n".join(lines)


class DocumentSection(BaseModel):
    section_id:       str
    title:            str
    content:          str
    section_type:     str
    word_count:       int       = 0
    confidence_score: float     = 0.0
    sources_used:     List[str] = Field(default_factory=list)
    compliance_flags: List[str] = Field(default_factory=list)
    revised:          bool      = False
    revision_count:   int       = 0
    generated_by:     str       = "groq"

    def model_post_init(self, __context: Any) -> None:
        if self.word_count == 0:
            self.word_count = len(self.content.split())


class ComplianceIssue(BaseModel):
    severity:       IssueSeverity
    category:       str
    section_id:     Optional[str] = None
    description:    str
    suggestion:     str
    regulatory_ref: Optional[str] = None
    rule_id:        Optional[str] = None


class ComplianceReport(BaseModel):
    overall_score:      float
    is_compliant:       bool
    issues:             List[ComplianceIssue] = Field(default_factory=list)
    guidelines_checked: List[str]             = Field(default_factory=list)
    entities_validated: Dict[str, List[str]]  = Field(default_factory=dict)
    missing_sections:   List[str]             = Field(default_factory=list)
    recommendations:    List[str]             = Field(default_factory=list)
    checked_at:         str                   = Field(default_factory=_utcnow)


# ── API Request / Response models ─────────────────────────────────────────────

class DocumentRequest(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    metadata:                 StudyMetadata
    document_type:            str           = DocumentType.CSP.value
    template_id:              Optional[str] = None
    language:                 str           = "en"
    include_compliance_check: bool          = True
    additional_context:       Optional[str] = None
    rag_top_k:                int           = 5
    model_tier:               str           = "medical"


class GenerationResponse(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    session_id:        str
    document_type:     str
    sections:          List[DocumentSection]
    compliance_report: ComplianceReport
    retrieved_sources: List[str]
    metadata:          StudyMetadata
    status:            str
    generated_at:      str
    model_used:        str = ""
    total_words:       int = 0

    def model_post_init(self, __context: Any) -> None:
        if self.total_words == 0:
            self.total_words = sum(s.word_count for s in self.sections)


class IngestResponse(BaseModel):
    success:        bool
    doc_id:         str
    filename:       str
    chunks_created: int
    message:        str


class FeedbackRequest(BaseModel):
    section_id:    Optional[str] = None
    reviewer_name: str
    reviewer_role: str              = "Medical Writer"
    comment:       str
    action:        FeedbackAction
    revised_text:  Optional[str]   = None
    severity:      str             = "minor"


class FeedbackLogEntry(BaseModel):
    """One entry written into the session feedback_log."""
    section_id:    Optional[str]
    reviewer:      str
    role:          str
    comment:       str
    action:        str
    revised_text:  Optional[str]
    rewritten:     bool   = False
    timestamp:     str    = Field(default_factory=_utcnow)


class FeedbackResponse(BaseModel):
    """Returned from POST /feedback/{session_id}."""
    success:           bool
    feedback_count:    int
    confidence_score:  Optional[float]      = None
    sections:          Optional[List[Any]]  = None
    updated_section:   Optional[Any]        = None
    section_analytics: Optional[List[Any]]  = None
    compliance_report:    Optional[Any]       = None
    doc_analytics:     Optional[Any]        = None  # document-level rollup


class PlaceholderFillRequest(BaseModel):
    """Request body for POST /placeholders/{session_id}."""
    replacements: Dict[str, str]  # {"INVESTIGATIONAL_PRODUCT": "TrialDrug-X 150mg", ...}


class PlaceholderFillResponse(BaseModel):
    """Returned from POST /placeholders/{session_id}."""
    success:              bool
    placeholders_found:   List[str]
    placeholders_filled:  int
    remaining:            List[str]   # any placeholders still unfilled
    sections_updated:     List[DocumentSection]
    compliance_report:    Optional[Any]       = None


class FinalizeRequest(BaseModel):
    document_name: Optional[str] = None    # md | json | docx


class FinalizeResponse(BaseModel):
    success:          bool
    session_id:       str
    status:           str
    compliance_score: float
    finalized_at:     str
    placeholders_remaining: List[str] = Field(default_factory=list)


class VectorStoreStats(BaseModel):
    retriever_type:              str
    total_documents:             int
    total_chunks:                int
    index_size:                  int
    sample_documents_loaded:     int  = 0
    regulatory_guidelines_loaded: int = 0


class HealthResponse(BaseModel):
    status:               str
    service:              str
    version:              str
    ollama_available:     bool
    ollama_model:         str
    ollama_host:          str = ""
    groq_available:       bool
    groq_fallback_model:  str = ""
    groq_validator_model: str = ""
    groq_role:            str
    active_generator:     str
    vector_store:         str
