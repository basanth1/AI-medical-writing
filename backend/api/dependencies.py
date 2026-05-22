"""
Dependency Injection container.
All services instantiated once and shared via FastAPI Depends().

LLMClient is the single entry point for all text generation —
services never import OllamaClient or GroqClient directly.
"""
from functools import lru_cache
from typing import List, Optional

from backend.core.config        import get_settings
from backend.core.llm_client    import LLMClient
from backend.services.rag_service         import RAGPipeline
from backend.services.generation_service  import DocumentGenerator
from backend.services.compliance_service  import ComplianceChecker
from backend.db.session_store             import SessionStore
from backend.db.finalized_store import FinalizedDocumentStore
from backend.services.pinecone_retriever import PineconeRetriever

@lru_cache
def get_llm_client() -> LLMClient:
    cfg = get_settings()
    return LLMClient(
        ollama_api_key = cfg.ollama_api_key,
        groq_api_key   = cfg.groq_api_key,
        ollama_model   = cfg.ollama_model or None,
        groq_model     = cfg.groq_model,
    )


@lru_cache
def get_rag_pipeline() -> RAGPipeline:
    cfg = get_settings()
    return RAGPipeline(vector_dim=cfg.vector_dim)


@lru_cache
def get_document_generator() -> DocumentGenerator:
    return DocumentGenerator(client=get_llm_client())


@lru_cache
def get_compliance_checker() -> ComplianceChecker:
    cfg = get_settings()
    return ComplianceChecker(enable_ner=cfg.enable_ner)


@lru_cache
def get_session_store() -> SessionStore:
    cfg = get_settings()
    return SessionStore(ttl_seconds=cfg.session_ttl_hours * 3600)


@lru_cache
def get_finalized_store() -> FinalizedDocumentStore:
    return FinalizedDocumentStore()


@lru_cache
def get_pinecone_retriever() -> Optional[PineconeRetriever]:
    cfg = get_settings()
    if not cfg.use_pinecone:
        return None
    if not cfg.pinecone_api_key:
        raise ValueError("USE_PINECONE=true but PINECONE_API_KEY is not set")
    return PineconeRetriever(
        api_key=cfg.pinecone_api_key,
        index_name=cfg.pinecone_index,
        ns_min_score=cfg.pinecone_min_score,
    )