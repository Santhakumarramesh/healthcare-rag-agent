"""
config.py — centralised settings loaded from .env
"""
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # OpenAI
    openai_api_key: str = "sk-placeholder"
    openai_model: str = "gpt-4o-mini"
    embedding_model: str = "text-embedding-3-small"

    # Pinecone
    pinecone_api_key: str = ""
    pinecone_index_name: str = "healthcare-rag"
    pinecone_environment: str = "us-east-1-aws"

    # Vector store
    vector_store_mode: str = "faiss"   # "faiss" | "pinecone"
    faiss_index_path: str = "data/faiss_index"

    # RAG
    chunk_size: int = 512
    chunk_overlap: int = 64
    top_k_retrieval: int = 5
    rerank_top_k: int = 3

    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    log_level: str = "INFO"

    class Config:
        env_file = ".env"
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
