"""
backend/services/rag_service.py
RAG Pipeline — ingestion, embedding, FAISS persistence, retrieval.

Storage design
──────────────
Each USER-INGESTED document gets its OWN folder under backend/db/faiss_indexes/:

    backend/db/faiss_indexes/
    └── <doc_id>/
        ├── index.faiss      ← FAISS IndexFlatIP (the vector embeddings)
        ├── chunks.json      ← chunk texts + metadata (parallel to the index)
        └── document.json    ← document-level metadata

Key design decisions
────────────────────
1. ONE save per document, called once after ALL chunks are embedded — not per chunk.
2. FAISS is kept as a SINGLE merged index in RAM for fast retrieval.
   Each document's on-disk index is loaded at startup and merged into the global index.
3. Built-in sample documents are NEVER written to disk — they are always
   reconstructed from backend/data/sample_documents.py on startup.
4. _chunk_texts / _chunk_meta stay in sync with the global FAISS index
   by appending in the same loop that calls index.add().

Restart sequence
────────────────
  __init__
    │
    ├─ _init_retriever()          → fresh empty FAISS index in RAM
    ├─ _load_builtin_docs()       → embed + add to RAM (no disk I/O)
    └─ _restore_persisted_docs()  → for each doc_id folder on disk:
                                      load doc's faiss index → merge into global
                                      load chunks.json → append to _chunk_texts/_chunk_meta
                                      load document.json → append to _documents
"""
from __future__ import annotations

import json
import os
import hashlib
import logging
import uuid
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)

# ── Data imports ──────────────────────────────────────────────────────────────
from backend.data.regulatory_guidelines import get_guidelines
from backend.data.sample_documents      import SAMPLE_DOCUMENTS

# ── Optional ML imports ───────────────────────────────────────────────────────
try:
    import numpy as np
    _NP = True
except ImportError:
    _NP = False

try:
    import faiss
    _FAISS = True
except ImportError:
    _FAISS = False
    logger.warning("faiss-cpu not installed — using TF-IDF fallback")

try:
    from sentence_transformers import SentenceTransformer
    _ST = True
except ImportError:
    _ST = False

try:
    import pdfplumber
    _PDF = True
except ImportError:
    _PDF = False


# ── Folder layout constants ───────────────────────────────────────────────────
_DB_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "db", "faiss_indexes")
)
_INDEX_FILE    = "index.faiss"   # FAISS vectors for this document
_CHUNKS_FILE   = "chunks.json"   # list of {text, metadata} for each chunk
_DOCUMENT_FILE = "document.json" # document-level metadata

# Built-in doc IDs — these are never written to disk
_BUILTIN_IDS = frozenset(doc["id"] for doc in SAMPLE_DOCUMENTS)


# ── TF-IDF fallback ───────────────────────────────────────────────────────────

class _TFIDFRetriever:
    """Keyword-based fallback when FAISS/sentence-transformers are unavailable."""

    def __init__(self):
        self._docs: List[Dict] = []
        self._mat  = None
        self._vec  = None

    def add(self, text: str, meta: dict) -> str:
        doc_id = uuid.uuid4().hex[:8]
        self._docs.append({"id": doc_id, "content": text, "metadata": meta})
        self._rebuild()
        return doc_id

    def _rebuild(self):
        try:
            from sklearn.feature_extraction.text import TfidfVectorizer
            self._vec = TfidfVectorizer(max_features=5000, stop_words="english")
            self._mat = self._vec.fit_transform(
                [d["content"] for d in self._docs]
            )
        except Exception:
            pass

    def search(self, query: str, top_k: int = 5) -> List[Dict]:
        if not self._docs:
            return []
        if self._vec and self._mat is not None:
            try:
                from sklearn.metrics.pairwise import cosine_similarity
                import numpy as np
                scores = cosine_similarity(
                    self._vec.transform([query]), self._mat
                )[0]
                idxs = np.argsort(scores)[::-1][:top_k]
                return [
                    {
                        "content":  self._docs[i]["content"],
                        "metadata": self._docs[i]["metadata"],
                        "score":    float(scores[i]),
                    }
                    for i in idxs if scores[i] > 0
                ]
            except Exception:
                pass
        # Keyword overlap fallback
        qw = set(query.lower().split())
        scored = sorted(
            self._docs,
            key=lambda d: len(qw & set(d["content"].lower().split())),
            reverse=True,
        )
        return [
            {"content": d["content"], "metadata": d["metadata"], "score": 0.5}
            for d in scored[:top_k]
        ]


# ── Main pipeline ─────────────────────────────────────────────────────────────

class RAGPipeline:
    """
    Ingestion → embedding → per-document FAISS persistence → merged retrieval.

    On-disk layout (one folder per user-ingested document):
        backend/db/faiss_indexes/
        └── <doc_id>/
            ├── index.faiss      ← FAISS vectors for this document's chunks
            ├── chunks.json      ← chunk texts and metadata (parallel list)
            └── document.json   ← document-level metadata

    In-memory:
        self._index         ← single merged FAISS index (all docs combined)
        self._chunk_texts   ← list of chunk strings, indexed by FAISS position
        self._chunk_meta    ← list of metadata dicts, indexed by FAISS position
        self._documents     ← document-level registry
    """

    def __init__(self, vector_dim: int = 384, db_root: str = _DB_ROOT):
        self.vector_dim   = vector_dim
        self.db_root      = db_root
        self._documents:   List[Dict]     = []
        self._chunk_count: Dict[str, int] = {}
        self._chunk_texts: List[str]      = []
        self._chunk_meta:  List[Dict]     = []

        os.makedirs(self.db_root, exist_ok=True)

        self.retriever_type = self._init_retriever()
        self._load_builtin_docs()     # always in-memory, never written to disk
        self._restore_persisted_docs()  # reload user-ingested docs from disk

        logger.info(
            f"RAGPipeline ready — retriever: {self.retriever_type} | "
            f"builtin: {len(SAMPLE_DOCUMENTS)} | "
            f"persisted: {len(self._documents) - len(SAMPLE_DOCUMENTS)} | "
            f"total chunks: {sum(self._chunk_count.values())}"
        )

    # ── Initialisation ────────────────────────────────────────────────────────

    def _init_retriever(self) -> str:
        if _FAISS and _ST and _NP:
            try:
                self._encoder = SentenceTransformer("all-MiniLM-L6-v2")
                self._index   = faiss.IndexFlatIP(self.vector_dim)
                logger.info("FAISS + SentenceTransformer initialised")
                return "faiss"
            except Exception as exc:
                logger.warning(f"FAISS init failed ({exc}) — using TF-IDF")
        self._fallback = _TFIDFRetriever()
        return "tfidf"

    def _load_builtin_docs(self):
        """
        Embed and add built-in sample documents to the in-memory index.
        These are NEVER written to disk — they are always reconstructed
        from backend/data/sample_documents.py on startup.
        """
        for doc in SAMPLE_DOCUMENTS:
            self._index_chunks_in_memory(
                doc["content"], doc["metadata"], doc["id"]
            )
        logger.info(f"Built-in docs loaded into RAM: {len(SAMPLE_DOCUMENTS)}")

    def _restore_persisted_docs(self):
        """
        Walk db_root, find every doc_id subfolder that has all three files,
        load the chunks into RAM, merge the FAISS index into the global index.
        Skips any folder whose doc_id matches a built-in document.
        """
        if self.retriever_type != "faiss":
            return

        restored = 0
        for doc_id in sorted(os.listdir(self.db_root)):
            folder = os.path.join(self.db_root, doc_id)
            if not os.path.isdir(folder):
                continue
            if doc_id in _BUILTIN_IDS:
                continue  # built-in — skip, already in RAM

            index_path    = os.path.join(folder, _INDEX_FILE)
            chunks_path   = os.path.join(folder, _CHUNKS_FILE)
            document_path = os.path.join(folder, _DOCUMENT_FILE)

            # All three files must exist for a valid persisted document
            if not all(os.path.isfile(p) for p in [index_path, chunks_path, document_path]):
                logger.warning(f"Incomplete persisted doc folder '{doc_id}' — skipping")
                continue

            try:
                # 1. Load the per-document FAISS index and merge into global index
                doc_index = faiss.read_index(index_path)
                self._index.add(
                    faiss.rev_swig_ptr(doc_index.get_xb(), doc_index.ntotal * self.vector_dim)
                    .reshape(doc_index.ntotal, self.vector_dim)
                    .astype("float32")
                )

                # 2. Load chunk texts + metadata and append to parallel lists
                with open(chunks_path, encoding="utf-8") as f:
                    chunks = json.load(f)   # list of {text, metadata}
                for chunk in chunks:
                    self._chunk_texts.append(chunk["text"])
                    self._chunk_meta.append(chunk["metadata"])

                # 3. Load document-level metadata
                with open(document_path, encoding="utf-8") as f:
                    doc_record = json.load(f)
                self._documents.append(doc_record)
                self._chunk_count[doc_id] = len(chunks)

                restored += 1
                logger.info(
                    f"Restored '{doc_id}': {len(chunks)} chunks from disk"
                )
            except Exception as exc:
                logger.error(
                    f"Failed to restore persisted doc '{doc_id}': {exc}"
                )

        if restored:
            logger.info(
                f"Persistence restore complete: {restored} doc(s), "
                f"{self._index.ntotal} total vectors in index"
            )

    # ── Chunking ──────────────────────────────────────────────────────────────

    @staticmethod
    def _chunk(text: str, size: int = 500, overlap: int = 50) -> List[str]:
        words, chunks, step = text.split(), [], max(1, size - overlap)
        for i in range(0, len(words), step):
            c = " ".join(words[i: i + size])
            if c.strip():
                chunks.append(c)
        return chunks or [text]

    # ── In-memory indexing (built-in docs, no disk I/O) ───────────────────────

    def _index_chunks_in_memory(self, text: str, meta: dict, doc_id: str):
        """
        Embed chunks and add to the global in-memory index only.
        Used for built-in sample documents.
        No files are written.
        """
        chunks = self._chunk(text)
        if self.retriever_type == "faiss":
            embs = self._encoder.encode(chunks, normalize_embeddings=True)
            self._index.add(embs.astype("float32"))
            for c in chunks:
                self._chunk_texts.append(c)
                self._chunk_meta.append({**meta, "doc_id": doc_id})
        else:
            for c in chunks:
                self._fallback.add(c, {**meta, "doc_id": doc_id})
        self._chunk_count[doc_id] = self._chunk_count.get(doc_id, 0) + len(chunks)

    # ── Persisted ingestion (user documents, saved to disk once) ─────────────

    def ingest(self, text: str, metadata: dict) -> str:
        """
        Ingest a user document.

        Steps:
          1. Chunk the text
          2. Embed all chunks in one batch
          3. Add embeddings to the global in-memory FAISS index
          4. Append chunk texts + metadata to the parallel lists
          5. Save everything to disk ONCE:
               db_root/<doc_id>/index.faiss   ← this doc's FAISS index (alone)
               db_root/<doc_id>/chunks.json   ← chunk texts + metadata
               db_root/<doc_id>/document.json ← document-level metadata
          6. Return the doc_id

        The global index is NOT written to disk — each document keeps its own
        FAISS index file so they can be loaded independently on restart.
        """
        doc_id = hashlib.md5(text[:200].encode()).hexdigest()[:12]

        # Check for duplicate (same content hash already ingested)
        if any(d["id"] == doc_id for d in self._documents):
            logger.info(f"Document '{doc_id}' already ingested — skipping")
            return doc_id

        chunks = self._chunk(text)

        if self.retriever_type == "faiss":
            # ── Step 1: embed all chunks in one batch ──────────────────────────
            embs = self._encoder.encode(chunks, normalize_embeddings=True)

            # ── Step 2: build a fresh per-document index (for disk storage) ────
            doc_index = faiss.IndexFlatIP(self.vector_dim)
            doc_index.add(embs.astype("float32"))

            # ── Step 3: merge into the global in-memory index ─────────────────
            self._index.add(embs.astype("float32"))

            # ── Step 4: append to parallel lists ──────────────────────────────
            chunk_records = []
            for c in chunks:
                chunk_meta = {**metadata, "doc_id": doc_id}
                self._chunk_texts.append(c)
                self._chunk_meta.append(chunk_meta)
                chunk_records.append({"text": c, "metadata": chunk_meta})

            # ── Step 5: write to disk ONCE ────────────────────────────────────
            self._persist_document(doc_id, doc_index, chunk_records, metadata)

        else:
            # TF-IDF path — no persistence
            for c in chunks:
                self._fallback.add(c, {**metadata, "doc_id": doc_id})

        # ── Step 6: register document ──────────────────────────────────────────
        doc_record = {"id": doc_id, "metadata": metadata}
        self._documents.append(doc_record)
        self._chunk_count[doc_id] = len(chunks)

        logger.info(
            f"Ingested doc '{doc_id}': {len(text)} chars, "
            f"{len(chunks)} chunks, saved to disk"
        )
        return doc_id

    def _persist_document(
        self,
        doc_id:        str,
        doc_index:     "faiss.Index",
        chunk_records: List[Dict],
        metadata:      dict,
    ) -> None:
        """
        Write all three files for one document to its own subfolder.
        Called ONCE per document — after ALL chunks have been embedded.
        """
        folder = os.path.join(self.db_root, doc_id)
        os.makedirs(folder, exist_ok=True)

        # index.faiss — only this document's vectors
        faiss.write_index(doc_index, os.path.join(folder, _INDEX_FILE))

        # chunks.json — parallel list of {text, metadata} for every chunk
        with open(os.path.join(folder, _CHUNKS_FILE), "w", encoding="utf-8") as f:
            json.dump(chunk_records, f, ensure_ascii=False, indent=2)

        # document.json — document-level metadata record
        doc_record = {"id": doc_id, "metadata": metadata}
        with open(os.path.join(folder, _DOCUMENT_FILE), "w", encoding="utf-8") as f:
            json.dump(doc_record, f, ensure_ascii=False, indent=2)

        logger.info(
            f"Persisted doc '{doc_id}': "
            f"{doc_index.ntotal} vectors, {len(chunk_records)} chunks"
        )

    # ── Retrieval ─────────────────────────────────────────────────────────────

    def retrieve(self, query: str, top_k: int = 5) -> List[Dict]:
        """
        Search the single merged in-memory FAISS index.
        All documents (builtin + user-ingested) are searched together.
        Returns top_k results sorted by cosine similarity score.
        """
        if self.retriever_type == "faiss":
            if self._index.ntotal == 0:
                return []
            try:
                q_emb = self._encoder.encode(
                    [query], normalize_embeddings=True
                )
                dists, idxs = self._index.search(
                    q_emb.astype("float32"), top_k
                )
                return [
                    {
                        "content":  self._chunk_texts[i],
                        "metadata": self._chunk_meta[i],
                        "score":    float(d),
                    }
                    for d, i in zip(dists[0], idxs[0])
                    if 0 <= i < len(self._chunk_texts)
                ]
            except Exception as exc:
                logger.error(f"FAISS search error: {exc}")
                return []
        return self._fallback.search(query, top_k)

    # ── Utilities ─────────────────────────────────────────────────────────────

    def extract_pdf(self, content: bytes) -> str:
        if _PDF:
            import io
            with pdfplumber.open(io.BytesIO(content)) as pdf:
                return "\n".join(p.extract_text() or "" for p in pdf.pages)
        return content.decode("latin-1", errors="ignore")

    def get_guidelines(self, doc_type: str, phase: str = "") -> str:
        return get_guidelines(doc_type, phase)

    def chunk_count(self, doc_id: str) -> int:
        return self._chunk_count.get(doc_id, 0)

    def list_persisted_docs(self) -> List[Dict]:
        """Return metadata for every user-ingested document on disk."""
        result = []
        for doc_id in sorted(os.listdir(self.db_root)):
            folder = os.path.join(self.db_root, doc_id)
            document_path = os.path.join(folder, _DOCUMENT_FILE)
            if os.path.isfile(document_path):
                try:
                    with open(document_path, encoding="utf-8") as f:
                        result.append(json.load(f))
                except Exception:
                    pass
        return result

    def delete_persisted_doc(self, doc_id: str) -> bool:
        """
        Remove a user-ingested document from disk.
        NOTE: the global in-memory index is NOT updated (FAISS IndexFlatIP
        does not support deletion). A full restart is needed for the deletion
        to be reflected in retrieval.
        """
        import shutil
        folder = os.path.join(self.db_root, doc_id)
        if os.path.isdir(folder):
            shutil.rmtree(folder)
            logger.info(
                f"Deleted persisted doc '{doc_id}' from disk. "
                "Restart the server to remove it from the in-memory index."
            )
            return True
        return False

    def stats(self) -> dict:
        persisted_count = sum(
            1 for d in os.listdir(self.db_root)
            if os.path.isdir(os.path.join(self.db_root, d))
            and os.path.isfile(os.path.join(self.db_root, d, _DOCUMENT_FILE))
        )
        idx_size = (
            self._index.ntotal
            if self.retriever_type == "faiss"
            else len(getattr(self._fallback, "_docs", []))
        )
        from backend.data.regulatory_guidelines import REGULATORY_GUIDELINES
        return {
            "retriever_type":              self.retriever_type,
            "total_documents":             len(self._documents),
            "builtin_documents":           len(SAMPLE_DOCUMENTS),
            "sample_documents_loaded":     len(SAMPLE_DOCUMENTS),
            "persisted_documents":         persisted_count,
            "total_chunks":                sum(self._chunk_count.values()),
            "index_size":                  idx_size,
            "regulatory_guidelines_loaded": len(REGULATORY_GUIDELINES),
            "db_root":                     self.db_root,
        }
