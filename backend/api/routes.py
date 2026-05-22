"""
API Routers — all HTTP endpoints.

Routes:
    /health           GET
    /ingest/document  POST
    /ingest/metadata  POST
    /generate         POST
    /sessions/{id}    GET
    /feedback/{id}    POST
    /finalize/{id}    POST
    /compliance/{id}  POST
    /templates        GET
    /vector-store     GET
"""

from __future__ import annotations
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query
from fastapi.responses import Response
import asyncio
from datetime import datetime, timezone
import logging
from fastapi import Body
from backend.core.models import (
    StudyMetadata, DocumentRequest, GenerationResponse,
    ComplianceReport, FeedbackRequest, FeedbackResponse,
    FeedbackLogEntry,
    PlaceholderFillRequest, PlaceholderFillResponse,
    FinalizeRequest, FinalizeResponse,
    IngestResponse, VectorStoreStats, HealthResponse, DocumentSection,
)
from backend.core.llm_client  import LLMClient
from backend.services.rag_service import RAGPipeline
from backend.services.generation_service import DocumentGenerator
from backend.services.compliance_service import ComplianceChecker
from backend.db.session_store import SessionStore
from backend.api.dependencies import (
    get_llm_client, get_rag_pipeline,
    get_document_generator, get_compliance_checker,
    get_session_store, get_finalized_store, get_pinecone_retriever,
)

from backend.utils.helpers import (
    extract_placeholders_from_sections,
    apply_placeholder_replacements,
    document_to_markdown,
    document_to_json,
    document_to_docx,
)
from backend.db.finalized_store import FinalizedDocumentStore
from backend.services.pinecone_retriever import PineconeRetriever
from typing import Optional

logger = logging.getLogger(__name__)
router = APIRouter()


# ── Health ────────────────────────────────────────────────────────────────────

@router.get("/health", response_model=HealthResponse)
async def health(
    llm: LLMClient    = Depends(get_llm_client),
    rag: RAGPipeline  = Depends(get_rag_pipeline),
):
    s = llm.status()
    return HealthResponse(
        status               = "healthy",
        service              = "Clinical Trial Document Generation API",
        version              = "1.0.0",
        ollama_available     = s["ollama"]["available"],
        ollama_model         = s["ollama"]["model"],
        ollama_host          = s["ollama"]["host"],
        groq_available       = s["groq"]["available"],
        groq_fallback_model  = s["groq"].get("fallback_model", ""),
        groq_validator_model = s["groq"].get("validator_model", "llama-3.1-8b-instant"),
        groq_role            = s["groq"]["role"],
        active_generator     = s["active_generator"],
        vector_store         = rag.retriever_type,
    )


# ── Ingestion ─────────────────────────────────────────────────────────────────

@router.post("/ingest/document", response_model=IngestResponse)
async def ingest_document(
    file:     UploadFile = File(...),
    doc_type: str        = Query("historical_trial"),
    rag:      RAGPipeline = Depends(get_rag_pipeline),
):
    content = await file.read()
    if file.filename.lower().endswith(".pdf"):
        text = rag.extract_pdf(content)
    else:
        text = content.decode("utf-8", errors="ignore")

    doc_id = rag.ingest(text, metadata={
        "filename": file.filename,
        "doc_type": doc_type,
        "ingested_at": datetime.now(timezone.utc).isoformat(),
    })
    return IngestResponse(
        success        = True,
        doc_id         = doc_id,
        filename       = file.filename,
        chunks_created = rag.chunk_count(doc_id),
        message        = f"'{file.filename}' ingested successfully",
    )


@router.post("/ingest/metadata", response_model=IngestResponse)
async def ingest_metadata(
    metadata: StudyMetadata,
    rag:      RAGPipeline = Depends(get_rag_pipeline),
):
    doc_id = rag.ingest(metadata.to_query_text(), metadata={
        "type":       "study_metadata",
        "indication": metadata.indication,
        "phase":      metadata.phase,
    })
    return IngestResponse(
        success        = True,
        doc_id         = doc_id,
        filename       = "metadata",
        chunks_created = rag.chunk_count(doc_id),
        message        = "Study metadata ingested",
    )


# ── Document Generation ───────────────────────────────────────────────────────

@router.post("/generate", response_model=GenerationResponse)
async def generate_document(
    request:    DocumentRequest,
    rag:        RAGPipeline      = Depends(get_rag_pipeline),
    generator:  DocumentGenerator = Depends(get_document_generator),
    checker:    ComplianceChecker = Depends(get_compliance_checker),
    store:      SessionStore      = Depends(get_session_store),
    llm:        LLMClient         = Depends(get_llm_client),
    pinecone:   Optional[PineconeRetriever] = Depends(get_pinecone_retriever),
):
    ts         = datetime.now(timezone.utc)
    session_id = (f"SES-{request.metadata.indication[:3].upper()}-"
                  f"{request.metadata.phase.replace(' ','').replace('Phase','P')}-"
                  f"{ts.strftime('%Y%m%d%H%M%S')}")

    logger.info(f"[{session_id}] Starting generation: {request.document_type}")

    # 1. Retrieve context
    query          = request.metadata.to_query_text()
    retrieved_docs = rag.retrieve(query, top_k=request.rag_top_k)
    guidelines     = rag.get_guidelines(request.document_type, request.metadata.phase)
    logger.debug("[%s] Retrieved %s documents for generation", session_id, len(retrieved_docs))
    # 2. Generate sections
    sections = await generator.generate(
        metadata      = request.metadata,
        document_type = request.document_type,
        retrieved_docs = retrieved_docs,
        guidelines    = guidelines,
        pinecone_retriever = pinecone,
    )

    # 3. RAG enrichment loop
    sections = await generator.rag_enrich(sections, rag, request.metadata)

    # 4. Compliance validation
    compliance = (
        checker.validate(sections, request.document_type, request.metadata)
        if request.include_compliance_check
        else ComplianceReport(overall_score=0, is_compliant=False,
                               guidelines_checked=[], checked_at=ts.isoformat())
    )
    section_dicts       = [s.model_dump() for s in sections]
    placeholders_found  = extract_placeholders_from_sections(section_dicts)
    # 5. Persist session
    store.set(session_id, {
        "session_id":    session_id,
        "metadata":      request.metadata.model_dump(),
        "document_type": request.document_type,
        "sections":      section_dicts,
        "compliance":    compliance.model_dump(),
        "retrieved_docs": [d["metadata"] for d in retrieved_docs],
        "feedback_log":     [],                                          # ← add this
    "placeholders_found": placeholders_found,
        "status":        "pending_review",
        "created_at":    ts.isoformat(),
        "model_used":    llm._groq.model_name if llm._groq.is_available() else llm._ollama.model,
    })

    logger.info(f"[{session_id}] Done — {len(sections)} sections, "
                f"score={compliance.overall_score}")

    return GenerationResponse(
        session_id        = session_id,
        document_type     = request.document_type,
        sections          = sections,
        compliance_report = compliance,
        retrieved_sources = [d.get("metadata", {}).get("filename",
                              d.get("metadata", {}).get("id", "Source"))
                             for d in retrieved_docs],
        metadata          = request.metadata,
        status            = "generated",
        generated_at      = ts.isoformat(),
        model_used        = llm.status()["active_generator"],
    )


# ── Session management ────────────────────────────────────────────────────────

@router.get("/sessions/{session_id}")
async def get_session(session_id: str, store: SessionStore = Depends(get_session_store)):
    data = store.get(session_id)
    if not data:
        raise HTTPException(404, "Session not found or expired")
    return data


@router.post("/compliance/{session_id}", response_model=ComplianceReport)
async def run_compliance(
    session_id: str,
    store:      SessionStore      = Depends(get_session_store),
    checker:    ComplianceChecker = Depends(get_compliance_checker),
):
    data = store.get(session_id)
    if not data:
        raise HTTPException(404, "Session not found")
    sections = [DocumentSection(**s) for s in data["sections"]]
    metadata = StudyMetadata(**data["metadata"])
    report   = checker.validate(sections, data["document_type"], metadata)
    store.update(session_id, {"compliance": report.model_dump()})
    return report


@router.post("/feedback/{session_id}")
async def submit_feedback(
    session_id: str,
    feedback: FeedbackRequest,
    store: SessionStore = Depends(get_session_store),
    llm: LLMClient = Depends(get_llm_client),
    checker:    ComplianceChecker = Depends(get_compliance_checker),
):
    data = store.get(session_id)
    if not data:
        raise HTTPException(404, "Session not found")

    log = data.get("feedback_log", [])

    log.append({
        "section_id": feedback.section_id,
        "reviewer": feedback.reviewer_name,
        "role": feedback.reviewer_role,
        "comment": feedback.comment,
        "action": feedback.action.value,
        "revised_text": feedback.revised_text,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    })

    # # 🔥 APPLY LOGIC BASED ON ACTION
    # if feedback.section_id:

    #     # ✅ APPROVE → DO NOTHING
    #     if feedback.action.value == "approve":
    #         pass

    #     # ✏️ REVISE → REWRITE
    #     elif feedback.action.value == "revise":
    #         for sec in data["sections"]:
    #             if sec.get("section_id") == feedback.section_id:

    #                 # 1. Rewrite the section content
    #                 rewritten_text, new_conf_score = llm.rewrite_section(
    #                     sec["content"],
    #                     feedback.comment,
    #                     feedback.revised_text,
    #                     feedback.section_id
    #                 )

    #                 # 2. Run compliance check on THIS section only (fast — single Groq call)
    #                 section_compliance = llm.validate(
    #                     section_title   = sec.get("title", feedback.section_id),
    #                     section_content = rewritten_text,
    #                     doc_type        = data.get("document_type", "Clinical Study Protocol"),
    #                 )

    #                 # 3. Compute section-level analytics
    #                 section_analytics = {
    #                     "word_count_before": sec.get("word_count", 0),
    #                     "word_count_after":  len(rewritten_text.split()),
    #                     "confidence_before": sec.get("confidence_score", 0.0),
    #                     "confidence_after":  round(new_conf_score, 4),
    #                     "revision_count":    sec.get("revision_count", 0) + 1,
    #                     "is_compliant":      section_compliance.get("is_compliant", False),
    #                     "compliance_issues": section_compliance.get("issues", []),
    #                 }

    #                 # 4. Apply all updates to the section dict
    #                 sec["content"]          = rewritten_text
    #                 sec["revised"]          = True
    #                 sec["word_count"]       = section_analytics["word_count_after"]
    #                 sec["confidence_score"] = section_analytics["confidence_after"]
    #                 sec["revision_count"]   = section_analytics["revision_count"]
    #                 sec["compliance_flags"] = section_compliance.get("issues", [])
    #                 sec["section_compliant"]= section_compliance.get("is_compliant", False)
    #                 sec["analytics"]        = section_analytics

    #                 updated_sec = sec   # keep reference for response
    #                 break

    #     # ❌ REJECT → REMOVE SECTION
    #     elif feedback.action.value == "reject":
    #         data["sections"] = [
    #             sec for sec in data["sections"]
    #             if sec.get("section_id") != feedback.section_id
    #         ]

    # # ✅ SAVE UPDATED STATE
    # # store.update(session_id, {
    # #     "feedback_log": log,
    # #     "sections": data["sections"],
    # #     "status": "under_review"
    # # })
    # # ── Re-run compliance on updated sections (only if something changed) ────
    # updated_compliance = data.get("compliance")  # default: keep existing
    # if feedback.section_id and feedback.action.value in ("revise", "reject"):
    #     try:
    #         updated_sections_objs = [DocumentSection(**s) for s in data["sections"]]
    #         metadata_obj          = StudyMetadata(**data["metadata"])
    #         from backend.services.compliance_service import ComplianceChecker
    #         # Reuse the injected checker — but we need it here, so import lazily
    #         # (checker is already injected as a FastAPI dependency — pass it in)
    #         new_compliance = checker.validate(
    #             updated_sections_objs,
    #             data.get("document_type", "Clinical Study Protocol"),
    #             metadata_obj,
    #         )
    #         updated_compliance = new_compliance.model_dump()
    #     except Exception as exc:
    #         logger.warning(f"Compliance re-run failed after feedback: {exc}")

    # # ── Initialise variables that are only set inside the revise branch ──────
    # new_conf_score = None
    # updated_sec    = None

    # # Re-assign from revise branch locals if they exist
    # if feedback.action.value == "revise" and feedback.section_id:
    #     for s in data["sections"]:
    #         if s.get("section_id") == feedback.section_id:
    #             new_conf_score = s.get("confidence_score")
    #             updated_sec    = s
    #             break

    # # ✅ SAVE UPDATED STATE
    # store.update(session_id, {
    #     "feedback_log": log,
    #     "sections":     data["sections"],
    #     "compliance":   updated_compliance,   # ← persist refreshed compliance
    #     "status":       "under_review",
    # })
    # ── Initialize response variables ─────────────────────────────────────────
    new_conf_score  = None
    updated_sec     = None

    # ── Apply action ──────────────────────────────────────────────────────────
    if feedback.section_id:
        if feedback.action.value == "approve":
            pass

        elif feedback.action.value == "revise":
            for sec in data["sections"]:
                if sec.get("section_id") == feedback.section_id:
                    rewritten_text, new_conf_score = llm.rewrite_section(
                        sec["content"],
                        feedback.comment,
                        feedback.revised_text,
                        feedback.section_id
                    )
                    section_compliance = llm.validate(
                        section_title   = sec.get("title", feedback.section_id),
                        section_content = rewritten_text,
                        doc_type        = data.get("document_type", "Clinical Study Protocol"),
                    )
                    section_analytics = {
                        "word_count_before": sec.get("word_count", 0),
                        "word_count_after":  len(rewritten_text.split()),
                        "confidence_before": sec.get("confidence_score", 0.0),
                        "confidence_after":  round(new_conf_score, 4),
                        "revision_count":    sec.get("revision_count", 0) + 1,
                        "is_compliant":      section_compliance.get("is_compliant", False),
                        "compliance_issues": section_compliance.get("issues", []),
                    }
                    sec["content"]           = rewritten_text
                    sec["revised"]           = True
                    sec["word_count"]        = section_analytics["word_count_after"]
                    sec["confidence_score"]  = section_analytics["confidence_after"]
                    sec["revision_count"]    = section_analytics["revision_count"]
                    sec["compliance_flags"]  = section_compliance.get("issues", [])
                    sec["section_compliant"] = section_compliance.get("is_compliant", False)
                    sec["analytics"]         = section_analytics
                    updated_sec = sec
                    break

        elif feedback.action.value == "reject":
            data["sections"] = [
                sec for sec in data["sections"]
                if sec.get("section_id") != feedback.section_id
            ]

    # ── Re-run full document compliance if something changed ──────────────────
    updated_compliance = data.get("compliance")
    if feedback.section_id and feedback.action.value in ("revise", "reject"):
        try:
            updated_sections_objs = [DocumentSection(**s) for s in data["sections"]]
            metadata_obj          = StudyMetadata(**data["metadata"])
            new_compliance = checker.validate(
                updated_sections_objs,
                data.get("document_type", "Clinical Study Protocol"),
                metadata_obj,
            )
            updated_compliance = new_compliance.model_dump()
        except Exception as exc:
            logger.warning(f"Compliance re-run failed after feedback: {exc}")

    # ── Persist ───────────────────────────────────────────────────────────────
    patch = {
        "feedback_log": log,
        "sections":     data["sections"],
        "status":       "under_review",
    }
    if updated_compliance is not None:
        patch["compliance"] = updated_compliance
    store.update(session_id, patch)

    all_section_analytics = [
        {
            "section_id":       s.get("section_id"),
            "title":            s.get("title"),
            "word_count":       s.get("word_count", 0),
            "confidence_score": s.get("confidence_score", 0.0),
            "revised":          s.get("revised", False),
            "revision_count":   s.get("revision_count", 0),
            "section_compliant":s.get("section_compliant"),
            "compliance_flags": s.get("compliance_flags", []),
        }
        for s in data["sections"]
    ]
    return FeedbackResponse(
    success           = True,
    feedback_count    = len(log),
    confidence_score  = new_conf_score if feedback.action.value == "revise" else None,
    sections          = data["sections"],
    # New fields — section-level detail
    updated_section   = updated_sec if feedback.action.value == "revise" else None,
    section_analytics = all_section_analytics,
    compliance_report = updated_compliance,
    doc_analytics     = {
        "total_sections":    len(data["sections"]),
        "revised_sections":  sum(1 for s in data["sections"] if s.get("revised")),
        "rejected_sections": sum(1 for f in log if f.get("action") == "reject"),
        "avg_confidence":    round(
            sum(s.get("confidence_score", 0) for s in data["sections"]) / max(len(data["sections"]), 1),
            4
        ),
        "total_words":       sum(s.get("word_count", 0) for s in data["sections"]),
        "feedback_count":    len(log),
    },
)


@router.get("/placeholders/{session_id}")
async def get_placeholders(
    session_id: str,
    store:      SessionStore = Depends(get_session_store),
):
    """
    Scan all section content and return every [PLACEHOLDER] token still present,
    together with a human-readable label where known.
    """
    from backend.utils.helpers import COMMON_PLACEHOLDERS

    data = store.get(session_id)
    if not data:
        raise HTTPException(404, "Session not found")

    remaining = extract_placeholders_from_sections(data["sections"])
    return {
        "session_id":   session_id,
        "placeholders": [
            {
                "token":       token,
                "label":       COMMON_PLACEHOLDERS.get(token, token.replace("_", " ").title()),
                "example":     COMMON_PLACEHOLDERS.get(token, ""),
            }
            for token in remaining
        ],
        "total": len(remaining),
    }

@router.post("/placeholders/{session_id}", response_model=PlaceholderFillResponse)
async def fill_placeholders(
    session_id: str,
    body:       PlaceholderFillRequest,
    store:      SessionStore = Depends(get_session_store),
    checker:    ComplianceChecker = Depends(get_compliance_checker),
):
    """
    Replace [PLACEHOLDER] tokens in all sections with user-supplied values.

    Body example:
        {
          "replacements": {
            "INVESTIGATIONAL_PRODUCT": "TrialDrug-X 150mg",
            "PRINCIPAL_INVESTIGATOR": "Dr. Jane Smith",
            "SPONSOR_NAME": "PharmaCo Inc."
          }
        }

    All sections are updated in the session store. Returns which placeholders
    were filled and which (if any) remain.
    """
    data = store.get(session_id)
    if not data:
        raise HTTPException(404, "Session not found")

    sections = data["sections"]
    # Detect before
    before = extract_placeholders_from_sections(sections)

    updated_sections, count, remaining = apply_placeholder_replacements(
        sections, body.replacements
    )
    logger.debug("[%s] Placeholder fill updated %s sections", session_id, len(updated_sections))
    store.update(session_id, {
        "sections":           updated_sections,
        "placeholders_found": remaining,
    })

    # filled = [t for t in before if t not in remaining]
    # logger.info(
    #     f"[{session_id}] Placeholders: filled {len(filled)}, remaining {len(remaining)}"
    # )
    # return PlaceholderFillResponse(
    #     success             = True,
    #     placeholders_found  = before,
    #     placeholders_filled = count,
    #     remaining           = remaining,
    #     sections_updated     = updated_sections,
    # )
    filled = [t for t in before if t not in remaining]

    # Re-run compliance on the placeholder-filled sections
    updated_compliance = data.get("compliance")
    if count > 0:
        try:
            updated_sections_objs = [DocumentSection(**s) for s in updated_sections]
            metadata_obj          = StudyMetadata(**data["metadata"])
            new_compliance = checker.validate(
                updated_sections_objs,
                data.get("document_type", "Clinical Study Protocol"),
                metadata_obj,
            )
            updated_compliance = new_compliance.model_dump()
            store.update(session_id, {"compliance": updated_compliance})
        except Exception as exc:
            logger.warning(f"Compliance re-run after placeholder fill failed: {exc}")

    logger.info(
        f"[{session_id}] Placeholders: filled {len(filled)}, remaining {len(remaining)}"
    )
    return PlaceholderFillResponse(
        success             = True,
        placeholders_found  = before,
        placeholders_filled = count,
        remaining           = remaining,
        sections_updated    = updated_sections,
        compliance_report   = updated_compliance,
    )

# @router.post("/finalize/{session_id}", response_model=FinalizeResponse)
# async def finalize_document(
#     session_id: str,
#     store:      SessionStore      = Depends(get_session_store),
#     checker:    ComplianceChecker = Depends(get_compliance_checker),
# ):
#     data = store.get(session_id)
#     if not data:
#         raise HTTPException(404, "Session not found")

#     sections = [DocumentSection(**s) for s in data["sections"]]
#     metadata = StudyMetadata(**data["metadata"])
#     final    = checker.validate(sections, data["document_type"], metadata)
#     ts       = datetime.now(timezone.utc).isoformat()
#     remaining_placeholders = extract_placeholders_from_sections(data["sections"])
#     store.update(session_id, {
#         "status":            "finalized",
#         "finalized_at":      ts,
#         "final_compliance":  final.model_dump(),
#         "remaining_placeholders": remaining_placeholders
#     })
#     logger.info(
#         f"[{session_id}] Finalized — score={final.overall_score}  "
#         f"placeholders_remaining={remaining_placeholders}"
#     )
#     return FinalizeResponse(
#         success          = True,
#         session_id       = session_id,
#         status           = "finalized",
#         compliance_score = final.overall_score,
#         finalized_at     = ts,
#         placeholders_remaining  = remaining_placeholders,
#     )

@router.post("/finalize/{session_id}", response_model=FinalizeResponse)
async def finalize_document(
    session_id:      str,
    body:            FinalizeRequest     = Body(default=FinalizeRequest()),
    store:           SessionStore        = Depends(get_session_store),
    checker:         ComplianceChecker   = Depends(get_compliance_checker),
    fin_store:       FinalizedDocumentStore = Depends(get_finalized_store),
):
    data = store.get(session_id)
    if not data:
        raise HTTPException(404, "Session not found")
 
    sections = [DocumentSection(**s) for s in data["sections"]]
    metadata = StudyMetadata(**data["metadata"])
    final    = checker.validate(sections, data["document_type"], metadata)
    ts       = datetime.now(timezone.utc).isoformat()
    remaining_placeholders = extract_placeholders_from_sections(data["sections"])
 
    # Determine human-readable document name
    # Body can optionally carry a custom name; fall back to document_type
    document_name = (
        getattr(body, "document_name", None)
        or data.get("document_name")
        or data.get("document_type", "Clinical Trial Document")
    )
 
    patch = {
        "status":                 "finalized",
        "finalized_at":           ts,
        "final_compliance":       final.model_dump(),
        "remaining_placeholders": remaining_placeholders,
        "document_name":          document_name,
    }
    store.update(session_id, patch)
 
    # ── Persist to disk ──────────────────────────────────────────────────────
    refreshed = store.get(session_id)
    fin_store.save(session_id, {
        **refreshed,
        "compliance_score": final.overall_score,
        "finalized_at":     ts,
        "document_name":    document_name,
    })
 
    logger.info(
        f"[{session_id}] Finalized & persisted — score={final.overall_score}  "
        f"placeholders_remaining={remaining_placeholders}"
    )
    return FinalizeResponse(
        success                  = True,
        session_id               = session_id,
        status                   = "finalized",
        compliance_score         = final.overall_score,
        finalized_at             = ts,
        placeholders_remaining   = remaining_placeholders,
    )

@router.get("/finalized-documents")
async def list_finalized_documents(
    fin_store: FinalizedDocumentStore = Depends(get_finalized_store),
):
    """Return lightweight summary list of all persisted finalized documents."""
    return {
        "documents": fin_store.list_all(),
        "total":     len(fin_store.list_all()),
    }
 
 
@router.get("/finalized-documents/{session_id}")
async def get_finalized_document(
    session_id: str,
    fin_store:  FinalizedDocumentStore = Depends(get_finalized_store),
):
    """Return the full record for one finalized document (all sections included)."""
    doc = fin_store.get(session_id)
    if not doc:
        raise HTTPException(404, "Finalized document not found")
    return doc
 
 
@router.delete("/finalized-documents/{session_id}")
async def delete_finalized_document(
    session_id: str,
    fin_store:  FinalizedDocumentStore = Depends(get_finalized_store),
):
    """Permanently delete a finalized document from disk."""
    deleted = fin_store.delete(session_id)
    if not deleted:
        raise HTTPException(404, "Finalized document not found")
    return {"success": True, "session_id": session_id}
 

@router.get("/export/{session_id}")
async def export_document(
    session_id: str,
    format:     str          = Query("md", description="md | json | docx"),
    store:      SessionStore = Depends(get_session_store),
):
    """
    Download the document in the requested format.

    md   → Markdown text (human-readable, tables preserved)
    json → Structured JSON (machine-readable, includes confidence scores)
    docx → Microsoft Word (tables rendered, cover page included)
    """
    data = store.get(session_id)
    if not data:
        raise HTTPException(404, "Session not found")

    doc_type  = data.get("document_type", "Clinical Trial Document")
    meta      = data.get("metadata", {})
    sections  = data.get("sections", [])
    compliance= data.get("compliance") or data.get("final_compliance")
    status    = data.get("status", "generated")
    safe_name = doc_type.replace(" ", "_")

    if format == "md":
        content  = document_to_markdown(doc_type, meta, sections, status)
        return Response(
            content          = content,
            media_type       = "text/markdown",
            headers          = {"Content-Disposition": f'attachment; filename="{safe_name}.md"'},
        )

    elif format == "json":
        content = document_to_json(session_id, doc_type, meta, sections, compliance, status)
        return Response(
            content    = content,
            media_type = "application/json",
            headers    = {"Content-Disposition": f'attachment; filename="{safe_name}.json"'},
        )

    elif format == "docx":
        loop    = asyncio.get_event_loop()
        content = await loop.run_in_executor(
            None,
            lambda: document_to_docx(doc_type, meta, sections, status),
        )
        return Response(
            content    = content,
            media_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            headers    = {"Content-Disposition": f'attachment; filename="{safe_name}.docx"'},
        )

    else:
        raise HTTPException(400, f"Unsupported format '{format}'. Use: md, json, docx.")
# ── Reference data ────────────────────────────────────────────────────────────

@router.get("/templates")
async def get_templates():
    return {
        "templates": [
            {"id": "csp", "name": "Clinical Study Protocol",
             "abbr": "CSP", "color": "#185FA5",
             "sections": ["intro","study_design","objectives","population",
                          "treatment","safety","statistics","ethics","data_management"],
             "regulatory_refs": ["ICH E6(R2)", "ICH E8", "FDA 21 CFR 312"]},
            {"id": "icf", "name": "Informed Consent Form",
             "abbr": "ICF", "color": "#0F6E56",
             "sections": ["purpose","procedures","risks","benefits",
                          "alternatives","confidentiality","voluntary","contact"],
             "regulatory_refs": ["ICH E6", "45 CFR 46", "FDA 21 CFR 50"]},
            {"id": "csr", "name": "Clinical Study Report",
             "abbr": "CSR", "color": "#993C1D",
             "sections": ["synopsis","introduction","study_design","patient_disposition",
                          "efficacy","safety","discussion","conclusions"],
             "regulatory_refs": ["ICH E3", "EMA Module 5"]},
            {"id": "sap", "name": "Statistical Analysis Plan",
             "abbr": "SAP", "color": "#6B3A8A",
             "sections": ["objectives","populations","sample_size","primary_analysis",
                          "secondary_analysis","safety_analysis","missing_data","interim_analysis"],
             "regulatory_refs": ["ICH E9", "ICH E9(R1)"]},
        ]
    }


@router.get("/vector-store", response_model=VectorStoreStats)
async def vector_store_stats(rag: RAGPipeline = Depends(get_rag_pipeline)):
    stats_data = rag.stats()
    logger.info(f"Stats data: {stats_data}")  # Log the stats
    return VectorStoreStats(**stats_data)
