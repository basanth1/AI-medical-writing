"""
Document Generation Service — section-by-section generation via LLMClient.
Uses Ollama (primary) → Groq (fallback) automatically via LLMClient.
"""
from __future__ import annotations
import asyncio, logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone

from backend.core.llm_client   import LLMClient
from backend.core.models       import StudyMetadata, DocumentSection
from backend.services.rag_service import RAGPipeline
from backend.data.section_templates import SECTION_MAP, SECTION_SYSTEMS, DEFAULT_SECTION_SYSTEM
from backend.services.pinecone_retriever import (
    PineconeRetriever,
    format_pinecone_context,
    SECTION_KEYWORDS,
)
from backend.utils.helpers import PLACEHOLDER_GENERATION_GUIDE
logger = logging.getLogger(__name__)


def _build_prompt_pinecone(
    sid:           str,
    title:         str,
    metadata,                    # StudyMetadata instance
    doc_type:      str,
    pinecone_ctx:  str,          # output of format_pinecone_context()
    guidelines:    str,
) -> str:
    """
    Section prompt that uses Pinecone-retrieved context instead of FAISS.

    Keeps the same INSTRUCTIONS block as _build_prompt() so LLM behaviour
    is identical — only the HISTORICAL CONTEXT block changes.

    Args:
        sid:          section id (e.g. 'population')
        title:        section title (e.g. '4. Study Population')
        metadata:     StudyMetadata instance (uses .to_prompt_context())
        doc_type:     e.g. 'Clinical Study Protocol'
        pinecone_ctx: formatted context from format_pinecone_context()
        guidelines:   regulatory guidelines string (same as FAISS path)
    """
    ctx   = pinecone_ctx[:2200] if len(pinecone_ctx) > 2200 else pinecone_ctx
    guide = guidelines[:1600]   if len(guidelines)  > 1600  else guidelines

    return f"""
==================== DOCUMENT GENERATION CONTEXT ====================

DOCUMENT TYPE : {doc_type}
SECTION       : {title}

-------------------- STUDY METADATA --------------------
{metadata.to_prompt_context()}

-------------------- HISTORICAL CONTEXT (Pinecone RAG) --------------------
{ctx or 'No historical context available.'}

-------------------- REGULATORY GUIDELINES --------------------
{guide or 'Standard GCP applies.'}

=====================================================================

INSTRUCTIONS (STRICT):

1. **STRUCTURE (MANDATORY)**
   - Organize the section into clear logical subsections.
   - Use:
     - Section headers (##, ###)
     - Bullet points (-)
     - Numbered lists (1,2,3)
   - Avoid large paragraphs.

2. **READABILITY**
   - Keep content easy to scan.
   - Break complex sentences into smaller parts.
   - Use bullet points wherever possible.

3. **TABLE FORMATTING (CRITICAL)**
   - If content involves schedules, comparisons, criteria, or structured data:
     → ALWAYS present as a Markdown table.
   - Table rules:
     - Proper headers
     - Aligned columns
     - No broken formatting
   - NEVER convert tables into paragraphs.

4. **CLINICAL WRITING STYLE**
   - Formal, regulatory-compliant language.
   - Third person (second person only for ICF).
   - No conversational tone.

5. **ACCURACY**
   - Do NOT alter any values from STUDY METADATA.
   - Follow ICH E6(R2) / GCP guidelines throughout.

6. **PLACEHOLDERS**
   - If a required value is missing, unknown, site-specific, document-specific, or patient/participant-specific, write a clear bracketed placeholder token in ALL_CAPS_WITH_UNDERSCORES.
   - Reuse the canonical placeholder names below whenever they fit; do not create a synonym such as [PI_NAME] when [PRINCIPAL_INVESTIGATOR] fits.
   - Do not invent real-looking names, phone numbers, emails, addresses, IDs, dates, or contact details.
   - Canonical placeholder list:
{PLACEHOLDER_GENERATION_GUIDE}
   - Use the same token consistently every time the same missing value is referenced.

Write ONLY the section content — no title, no preamble.
"""


def _build_prompt(
    sid: str,
    title: str,
    metadata: StudyMetadata,
    doc_type: str,
    context: str,
    guidelines: str
) -> str:
    
    ctx   = context[:2200] if len(context) > 2200 else context
    guide = guidelines[:1600] if len(guidelines) > 1600 else guidelines

    return f"""
==================== DOCUMENT GENERATION CONTEXT ====================

DOCUMENT TYPE : {doc_type}
SECTION       : {title}

-------------------- STUDY METADATA --------------------
{metadata.to_prompt_context()}

-------------------- HISTORICAL CONTEXT --------------------
{ctx or 'No historical context available.'}

-------------------- REGULATORY GUIDELINES --------------------
{guide or 'Standard GCP applies.'}

=====================================================================

INSTRUCTIONS (STRICT):

1. **STRUCTURE (MANDATORY)**
   - Organize the section into clear logical subsections.
   - Use:
     - Section headers (##, ###)
     - Bullet points (-)
     - Numbered lists (1,2,3)
   - Avoid large paragraphs.

2. **READABILITY**
   - Keep content easy to scan.
   - Break complex sentences into smaller parts.
   - Use bullet points wherever possible.

3. **TABLE FORMATTING (CRITICAL)**
   - If content involves schedules, comparisons, criteria, or structured data:
     → ALWAYS present as a Markdown table.
   - Table rules:
     - Proper headers
     - Aligned columns
     - No broken formatting
   - NEVER convert tables into paragraphs.

4. **CLINICAL WRITING STYLE**
   - Formal, regulatory-compliant language.
   - Third person (second person only for ICF).
   - No conversational tone.

5. **ACCURACY**
   - Do NOT alter:
     - Drug names
     - Dosages
     - Endpoints
   - Preserve all scientific meaning.

6. **PLACEHOLDERS**
   - If a required value is missing, unknown, site-specific, document-specific, or patient/participant-specific, write a clear bracketed placeholder token in ALL_CAPS_WITH_UNDERSCORES.
   - Reuse the canonical placeholder names below whenever they fit; do not create a synonym such as [PI_NAME] when [PRINCIPAL_INVESTIGATOR] fits.
   - Do not invent real-looking names, phone numbers, emails, addresses, IDs, dates, or contact details.
   - Canonical placeholder list:
{PLACEHOLDER_GENERATION_GUIDE}
   - Use the same token consistently every time the same missing value is referenced.

7. **OUTPUT FORMAT**
   - Output ONLY the final section.
   - Do NOT include explanations.
   - Ensure it looks like:
     → Clinical protocol / CSR ready
     → UI-friendly structured content

=====================================================================

TASK:
Write the complete "{title}" section for the {doc_type}.

=====================================================================
""".strip()

class DocumentGenerator:
    """
    Orchestrates section generation + RAG enrichment.
    Accepts LLMClient — which internally chooses Ollama or Groq.
    """

    def __init__(self, client: LLMClient):
        self.client = client
        status = client.status()
        logger.info(
            f"DocumentGenerator ready — "
            f"generator={status['active_generator']} "
            f"ollama={'✓' if status['ollama']['available'] else '✗'} "
            f"groq={'✓' if status['groq']['available'] else '✗'}"
        )

    async def generate(
        self,
        metadata:            "StudyMetadata",
        document_type:       str,
        retrieved_docs:      "List[Dict]",
        guidelines:          str,
        pinecone_retriever:  "Optional[PineconeRetriever]" = None,
    ) -> "List[DocumentSection]":
        """
        Generate all document sections (async wrapper over sync batch).

        When pinecone_retriever is provided:
        - Runs document selection once (probe phase)
        - Builds a per-section Pinecone prompt for each section
        - Falls back to FAISS context if Pinecone retrieval returns no chunks

        When pinecone_retriever is None:
        - Uses the existing FAISS _build_context() + _build_prompt() path
        """
        sections_tmpl = SECTION_MAP.get(document_type, SECTION_MAP["Clinical Study Protocol"])
        meta_query    = metadata.to_query_text()

        if pinecone_retriever is not None:
            # ── Pinecone path ──────────────────────────────────────────────────
            selected_docs = pinecone_retriever.select_documents(meta_query)
            prompts = []
            for sid, title in sections_tmpl:
                chunks = pinecone_retriever.retrieve_for_section(
                    meta_query, sid, selected_docs
                )
                if chunks:
                    pinecone_ctx = format_pinecone_context(chunks)
                    prompt = _build_prompt_pinecone(
                        sid, title, metadata, document_type, pinecone_ctx, guidelines
                    )
                    sources = list({c["source"] for c in chunks})
                else:
                    # No Pinecone chunks for this section — fall back to FAISS
                    logger.warning(
                        f"[generate] No Pinecone chunks for section '{sid}', "
                        "falling back to FAISS context."
                    )
                    faiss_ctx = self._build_context(retrieved_docs)
                    prompt    = _build_prompt(
                        sid, title, metadata, document_type, faiss_ctx, guidelines
                    )
                    sources = [
                        d.get("metadata", {}).get("filename", "Historical Document")
                        for d in retrieved_docs[:3]
                    ]
                prompts.append((sid, title, prompt, sources))
        else:
            # ── FAISS path (unchanged) ─────────────────────────────────────────
            context_str = self._build_context(retrieved_docs)
            source_names = [
                d.get("metadata", {}).get("filename",
                d.get("metadata", {}).get("id", "Historical Document"))
                for d in retrieved_docs[:3]
            ]
            prompts = [
                (sid, title,
                _build_prompt(sid, title, metadata, document_type, context_str, guidelines),
                source_names)
                for sid, title in sections_tmpl
            ]
        logger.debug("Built %s section generation prompts", len(prompts))
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self._batch_generate, prompts)

    async def rag_enrich(
        self,
        sections: List[DocumentSection],
        rag:      RAGPipeline,
        metadata: StudyMetadata,
    ) -> List[DocumentSection]:
        """RAG enrichment loop — improves each section with per-section retrieval."""
        if not self.client.is_available():
            return sections
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self._enrich_all, sections, rag, metadata)

    # ── Sync internals (run in executor) ──────────────────────────────────────

    def _batch_generate(
        self,
        prompts: "List[tuple]",  # each element: (sid, title, prompt, sources_list)
    ) -> "List[DocumentSection]":
        results = []
        total   = len(prompts)

        for i, (sid, title, prompt, source_names) in enumerate(prompts):
            logger.info(f"  [{i+1}/{total}] Generating: {title}")
            system = SECTION_SYSTEMS.get(sid, DEFAULT_SECTION_SYSTEM)
            try:
                content, conf_score, breakdown = self.client.generate_scored(
                    sid, prompt, system=system
                )
                logger.info(
                    f"  [{i+1}/{total}] ✓ {title} "
                    f"{breakdown.word_count} words  confidence={conf_score:.3f}"
                )
            except Exception as exc:
                logger.error(f"  [{i+1}/{total}] ✗ '{sid}' failed: {exc}")
                content    = (
                    f"[Generation failed for section '{title}'. "
                    "Check OLLAMA_API_KEY / GROQ_API_KEY and retry.]"
                )
                conf_score = 0.0
                breakdown  = None

            status  = self.client.status()
            gen_tag = (
                f"ollama/{self.client._ollama.model}"
                if status["ollama"]["available"]
                else f"groq/{self.client._groq.model_name}"
            )

            results.append(DocumentSection(
                section_id       = sid,
                title            = title,
                content          = content,
                section_type     = sid,
                confidence_score = conf_score,
                sources_used     = source_names,
                generated_by     = gen_tag,
            ))

        return results


    def _enrich_all(
        self,
        sections: List[DocumentSection],
        rag:      RAGPipeline,
        metadata: StudyMetadata,
    ) -> List[DocumentSection]:
        enriched = []
        total    = len(sections)

        for i, section in enumerate(sections):
            query = f"{section.title} {metadata.indication} {metadata.phase} {metadata.primary_endpoint}"
            extra = rag.retrieve(query, top_k=3)
            if not extra:
                enriched.append(section)
                continue

            logger.info(f"  RAG enrich [{i+1}/{total}]: {section.title}")
            extra_ctx = "\n---\n".join(d["content"][:400] for d in extra[:2])
            enrich_prompt = (
                f"You wrote this clinical trial document section:\n\n"
                f"--- CURRENT DRAFT ---\n{section.content[:1600]}\n\n"
                f"--- ADDITIONAL RETRIEVED CONTEXT ---\n{extra_ctx}\n\n"
                f"--- STUDY CONTEXT ---\n{metadata.to_prompt_context()}\n\n"
                "Improve the draft by:\n"
                "1. Adding important missing details from the retrieved context.\n"
                "2. Increasing specificity (lab thresholds, timepoints, statistical parameters).\n"
                "3. Ensuring ICH / FDA / EMA compliance language is present.\n"
                "4. Preserving all existing correct content.\n\n"
                "Return ONLY the improved section text, no preamble."
            )
            try:
                improved = self.client.generate_with_system(
                    SECTION_SYSTEMS.get(section.section_id, DEFAULT_SECTION_SYSTEM),
                    enrich_prompt,
                )
                section.content    = improved
                section.word_count = len(improved.split())
                section.sources_used = list(set(
                    section.sources_used +
                    [d.get("metadata", {}).get("doc_type", "RAG source") for d in extra[:2]]
                ))
            except Exception as exc:
                logger.warning(f"Enrichment skipped for '{section.section_id}': {exc}")

            enriched.append(section)

        return enriched

    @staticmethod
    def _build_context(docs: List[Dict]) -> str:
        parts = []
        for doc in docs:
            meta  = doc.get("metadata", {})
            label = f"{meta.get('doc_type','Document')} ({meta.get('indication','')} {meta.get('phase','')})"
            parts.append(f"Source: {label}\n{doc['content'][:600]}")
        return "\n\n---\n\n".join(parts)
