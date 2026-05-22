"""
Application configuration — reads from .env file or environment variables.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache
from typing import List


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── Ollama — PRIMARY generator (gpt-oss:120b) ─────────────────────────────
    ollama_api_key:  str   = ""
    ollama_host:     str   = "https://ollama.com"
    ollama_model:    str   = "gpt-oss:120b"    # confirmed model
    ollama_timeout:  int   = 180               # 120B needs more time

    # ── Groq — VALIDATOR (llama-3.1-8b) + FALLBACK (llama-3.3-70b) ──────────
    groq_api_key:     str   = ""
    groq_model:       str   = "medical"         # → llama-3.3-70b-versatile
    groq_temperature: float = 0.2
    groq_max_tokens:  int   = 2048

    # ── Vector store ──────────────────────────────────────────────────────────
    faiss_index_path: str  = "./data/faiss_index"
    vector_dim:       int  = 384
    chunk_size:       int  = 500
    chunk_overlap:    int  = 50
    rag_top_k:        int  = 5

        # ── Pinecone (optional) ─────────────────────────────────────────────────
    use_pinecone:     bool = False
    pinecone_api_key: str  = ""
    pinecone_index:   str  = "clinical-rag-index"
    pinecone_min_score: float = 0.45

    # ── API ───────────────────────────────────────────────────────────────────
    api_host:     str       = "127.0.0.1"
    api_port:     int       = 8765
    api_reload:   bool      = False
    cors_origins: List[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",]
    api_version:  str       = "1.0.0"

    # ── App ───────────────────────────────────────────────────────────────────
    log_level:         str  = "INFO"
    session_ttl_hours: int  = 24
    max_upload_mb:     int  = 50
    enable_ner:        bool = False
    # ── Auth ──────────────────────────────────────────────────────────────────
    admin_username: str = "admin"
    admin_password: str = ""
    user_username:  str = "user"
    user_password:  str = ""
    frontend_url:   str = "http://localhost:5173"

@lru_cache
def get_settings() -> Settings:
    return Settings()
