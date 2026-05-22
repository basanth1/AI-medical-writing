"""
backend/services/pinecone_retriever.py

Section-aware Pinecone retriever for clinical trial document generation.

Namespace structure (auto-discovered from live index stats):
    {doc}_sections  →  one vector per section (section-level summaries)
    {doc}_chunks    →  many vectors per section (paragraph-level chunks)

Retrieval strategy per section:
    Pass 1: query _sections  → structural framing + tone
    Pass 2: query _chunks    → specific values, criteria, stats

Usage in generation_service.py:
    retriever     = PineconeRetriever(api_key, index_name)
    selected_docs = retriever.select_documents(metadata.to_query_text())
    for sid, title in section_list:
        chunks = retriever.retrieve_for_section(
                     metadata.to_query_text(), sid, selected_docs
                 )
        prompt = build_pinecone_prompt(sid, title, metadata, doc_type, chunks)
"""

from __future__ import annotations

import logging
import os
import time
from typing import Dict, List, Optional, Tuple

from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)

# ── Section-specific retrieval keywords ───────────────────────────────────────
# Prepended to the metadata query before embedding so the vector lands in the
# semantic neighbourhood of that section type — works even when stored chunks
# have no section_type metadata tag.
SECTION_KEYWORDS: Dict[str, str] = {
    "intro":
        "introduction background rationale disease overview pathophysiology unmet need",
    "study_design":
        "study design randomized controlled double-blind treatment arms blinding multicenter",
    "objectives":
        "primary endpoint secondary endpoint objectives efficacy outcome measure",
    "population":
        "inclusion exclusion criteria patient population eligibility diagnosis age",
    "treatment":
        "dosage dose regimen administration route treatment duration investigational product",
    "safety":
        "adverse events safety monitoring SAE DSMB stopping rules tolerability",
    "statistics":
        "statistical analysis sample size power calculation ITT per-protocol",
    "ethics":
        "informed consent IRB ethics committee regulatory GCP ICH E6",
    "data_management":
        "data collection CRF EDC database quality control monitoring",
}


class PineconeRetriever:
    """
    Namespace-aware, section-targeted Pinecone retriever.

    The retriever is initialised once (via lru_cache in dependencies.py)
    and shared across all requests.  It is safe to call from async context
    because all Pinecone SDK calls are synchronous and run in an executor.

    Args:
        api_key:       Pinecone API key
        index_name:    Pinecone index name (e.g. 'clinical-rag-index')
        embed_model:   SentenceTransformer model name — must match what was
                       used to build the index (default: BAAI/bge-base-en-v1.5)
        ns_min_score:  Minimum cosine similarity for a document to be selected
                       during the probe phase. Lower → more documents selected.
    """

    EMBED_MODEL = "BAAI/bge-base-en-v1.5"

    def __init__(
        self,
        api_key:      str,
        index_name:   str,
        embed_model:  str   = EMBED_MODEL,
        ns_min_score: float = 0.45,
    ):
        from pinecone import Pinecone as PineconeClient

        self._pc           = PineconeClient(api_key=api_key)
        self._index        = self._pc.Index(index_name)
        self._ns_min_score = ns_min_score

        # Load encoder (same model used when building the index)
        logger.info(f"[PineconeRetriever] Loading encoder: {embed_model}")
        self._encoder = SentenceTransformer(embed_model)

        # Auto-discover namespace pairs from live index stats — zero hardcoding
        self._ns_pairs: Dict[str, Tuple[str, str]] = {}
        self._refresh_ns_pairs()

        logger.info(
            f"[PineconeRetriever] Ready — {len(self._ns_pairs)} document(s): "
            f"{list(self._ns_pairs.keys())}"
        )

    # ── Public API ─────────────────────────────────────────────────────────────

    def select_documents(
        self,
        metadata_query: str,
        max_docs:       int = 3,
    ) -> List[Dict]:
        """
        Probe every _sections namespace with the metadata query and return
        the most relevant documents.  Runs once per generation request.

        Args:
            metadata_query: output of StudyMetadata.to_query_text()
            max_docs:       hard cap on documents returned

        Returns:
            List of dicts sorted by relevance:
            [{'doc_key', 'sections_ns', 'chunks_ns', 'top_score'}, ...]
        """
        vec    = self._embed(metadata_query)
        scored = []

        for doc_key, (sections_ns, chunks_ns) in self._ns_pairs.items():
            try:
                resp = self._index.query(
                    vector=vec, top_k=5,
                    include_metadata=False,
                    namespace=sections_ns,
                )
                hits = resp.get("matches", [])
                if hits:
                    top_score = max(m["score"] for m in hits)
                    scored.append({
                        "doc_key":     doc_key,
                        "sections_ns": sections_ns,
                        "chunks_ns":   chunks_ns,
                        "top_score":   round(top_score, 4),
                    })
            except Exception as exc:
                logger.warning(f"[PineconeRetriever] Probe failed ns={sections_ns}: {exc}")

        scored.sort(key=lambda x: x["top_score"], reverse=True)

        selected = [d for d in scored if d["top_score"] >= self._ns_min_score][:max_docs]

        if not selected and scored:
            # Safe fallback: always return at least the best-matching document
            logger.warning(
                "[PineconeRetriever] No document met ns_min_score "
                f"({self._ns_min_score}). Falling back to top-1."
            )
            selected = scored[:1]

        logger.info(
            f"[PineconeRetriever] Selected documents: "
            f"{[d['doc_key'] for d in selected]}"
        )
        return selected

    def retrieve_for_section(
        self,
        metadata_query: str,
        section_id:     str,
        selected_docs:  List[Dict],
        top_k_sections: int   = 3,
        top_k_chunks:   int   = 5,
        min_score:      float = 0.30,
        max_total:      int   = 8,
    ) -> List[Dict]:
        """
        Two-pass retrieval for one document section.

        Pass 1 — _sections namespaces: retrieves section-level summaries that
                  match the section type AND the study topic.  Gives the LLM
                  structural framing and regulatory tone.

        Pass 2 — _chunks namespaces: retrieves paragraph-level chunks with
                  specific clinical values (doses, criteria, stats, etc.).

        Both passes use the same composite query:
            "{section_keywords} | {metadata_query}"

        Args:
            metadata_query: output of StudyMetadata.to_query_text()
            section_id:     key from SECTION_KEYWORDS (e.g. 'population')
            selected_docs:  output of select_documents() — already filtered
            top_k_sections: hits per _sections namespace
            top_k_chunks:   hits per _chunks namespace
            min_score:      discard chunks below this cosine similarity
            max_total:      cap on merged result list

        Returns:
            List of chunk dicts sorted by score descending:
            [{'content', 'metadata', 'score', 'chunk_type', 'source'}, ...]
            chunk_type is 'section_summary' or 'paragraph'
        """
        keywords = SECTION_KEYWORDS.get(section_id, "")
        query    = f"{keywords} | {metadata_query}" if keywords else metadata_query
        vec      = self._embed(query)
        seen: Dict[str, Dict] = {}

        def _query_ns(namespace: str, top_k: int, chunk_type: str) -> None:
            try:
                resp = self._index.query(
                    vector=vec, top_k=top_k,
                    include_metadata=True,
                    namespace=namespace,
                )
                for m in resp.get("matches", []):
                    if m["score"] < min_score:
                        continue
                    vid  = m["id"]
                    meta = m.get("metadata", {})
                    chunk = {
                        "content":    meta.get("text", meta.get("content", "")),
                        "metadata":   meta,
                        "score":      round(m["score"], 4),
                        "chunk_type": chunk_type,
                        "source":     meta.get(
                            "filename",
                            meta.get("source", namespace.split("_")[0])
                        ),
                    }
                    # Keep highest-scoring copy when same id appears in multiple ns
                    if vid not in seen or chunk["score"] > seen[vid]["score"]:
                        seen[vid] = chunk
            except Exception as exc:
                logger.warning(
                    f"[PineconeRetriever] Retrieve failed ns={namespace}: {exc}"
                )

        # Pass 1: structural context from _sections
        for doc in selected_docs:
            _query_ns(doc["sections_ns"], top_k_sections, "section_summary")

        # Pass 2: detailed content from _chunks
        for doc in selected_docs:
            _query_ns(doc["chunks_ns"], top_k_chunks, "paragraph")

        results = sorted(seen.values(), key=lambda x: x["score"], reverse=True)
        return results[:max_total]

    # ── Helpers ────────────────────────────────────────────────────────────────

    def _embed(self, text: str) -> List[float]:
        """Embed one string with L2 normalisation."""
        return self._encoder.encode(
            [text], normalize_embeddings=True
        )[0].tolist()

    def _refresh_ns_pairs(self) -> None:
        """
        Discover namespace pairs from live index stats.
        Called at init; call again if new documents are ingested into Pinecone.
        """
        try:
            stats  = self._index.describe_index_stats()
            all_ns = set(stats.get("namespaces", {}).keys())
            pairs  = {}
            for ns in all_ns:
                if ns.endswith("_sections"):
                    doc_key   = ns[: -len("_sections")]
                    chunks_ns = f"{doc_key}_chunks"
                    if chunks_ns in all_ns:
                        pairs[doc_key] = (ns, chunks_ns)
            self._ns_pairs = pairs
        except Exception as exc:
            logger.error(f"[PineconeRetriever] Failed to refresh ns pairs: {exc}")


def format_pinecone_context(chunks: List[Dict], max_chars: int = 500) -> str:
    """
    Format retrieved Pinecone chunks into a two-part reference block
    for inclusion in the LLM generation prompt.

    Section summaries come first (structural framing), then paragraph
    chunks (detailed content).  Each is numbered and labelled.

    Args:
        chunks:    output of PineconeRetriever.retrieve_for_section()
        max_chars: truncate each chunk text to this many characters

    Returns:
        Formatted string ready to embed in _build_prompt().
    """
    section_chunks = [c for c in chunks if c["chunk_type"] == "section_summary"]
    content_chunks = [c for c in chunks if c["chunk_type"] == "paragraph"]

    if not chunks:
        return "No relevant reference material found in Pinecone knowledge base."

    lines   = []
    counter = 1

    if section_chunks:
        lines.append("--- Section-Level Context (structure and framing) ---")
        for c in section_chunks:
            text = c["content"].strip().replace("\n", " ")
            text = text[:max_chars] + ("..." if len(text) > max_chars else "")
            lines.append(f"[REF {counter}] source={c['source']}  score={c['score']}")
            lines.append(text)
            lines.append("")
            counter += 1

    if content_chunks:
        lines.append("--- Detailed Content (specific values and language) ---")
        for c in content_chunks:
            text = c["content"].strip().replace("\n", " ")
            text = text[:max_chars] + ("..." if len(text) > max_chars else "")
            lines.append(f"[REF {counter}] source={c['source']}  score={c['score']}")
            lines.append(text)
            lines.append("")
            counter += 1

    return "\n".join(lines)
