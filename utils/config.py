"""
Centralized configuration management using environment variables.
"""
import os
import secrets
from dotenv import load_dotenv
from loguru import logger

load_dotenv()

class Config:
    # OpenAI
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    NVIDIA_API_KEY: str = os.getenv("NVIDIA_API_KEY", "")
    NVIDIA_MODEL: str = os.getenv("NVIDIA_MODEL", "meta/llama-3.1-405b-instruct")
    NVIDIA_RERANK_MODEL: str = os.getenv("NVIDIA_RERANK_MODEL", "nvidia/llama-nemotron-rerank-1b-v2")

    # Embeddings
    # Default: S-BioBERT — medical-domain sentence embeddings (PubMed + SNLI trained)
    # Fallback set via env var to any sentence-transformers model or OpenAI
    EMBEDDING_MODEL: str = os.getenv(
        "EMBEDDING_MODEL", "pritamdeka/S-BioBert-snli-multinli-stsb"
    )

    # Vector Store
    FAISS_INDEX_PATH: str = os.getenv("FAISS_INDEX_PATH", "./vectorstore/faiss_index")
    VECTOR_STORE_TYPE: str = os.getenv("VECTOR_STORE_TYPE", "faiss")

    # Pinecone (optional)
    PINECONE_API_KEY: str = os.getenv("PINECONE_API_KEY", "")
    PINECONE_INDEX_NAME: str = os.getenv("PINECONE_INDEX_NAME", "healthcare-rag")
    PINECONE_ENVIRONMENT: str = os.getenv("PINECONE_ENVIRONMENT", "us-east-1")

    # Tavily web search (optional)
    TAVILY_API_KEY: str = os.getenv("TAVILY_API_KEY", "")

    # Retrieval
    MAX_RETRIEVED_DOCS: int = int(os.getenv("MAX_RETRIEVED_DOCS", "5"))
    EVAL_SAMPLE_SIZE: int = 20
    
    # Hybrid Search
    RRF_K: int = 60
    RERANK_TOP_K: int = int(os.getenv("RERANK_TOP_K", "3"))
    CONFIDENCE_THRESHOLD: float = float(os.getenv("CONFIDENCE_THRESHOLD", "0.6"))

    # Local LLM (AirLLM privacy mode)
    LOCAL_MODE: bool = os.getenv("LOCAL_MODE", "false").lower() == "true"
    LOCAL_MODEL_ID: str = os.getenv(
        "LOCAL_MODEL_ID",
        "mlx-community/Meta-Llama-3-8B-Instruct-4bit"
    )

    # API
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
    # Render sets PORT; local .env might set API_PORT.
    # We prioritize PORT to ensure Render's load balancer can reach the app.
    API_PORT: int = int(os.getenv("PORT") or os.getenv("API_PORT") or "8000")

    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    APP_ENV: str = os.getenv("APP_ENV", "development")

    # Security
    # JWT secret key — defaults to a random value if not set (tokens won't survive restarts).
    # Set a stable value via env var in production.
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY") or secrets.token_urlsafe(32)

    # Comma-separated allowed CORS origins.
    # Use "*" only for local dev; always restrict in production.
    CORS_ORIGINS: str = os.getenv("CORS_ORIGINS", "*")

    # Error monitoring (optional)
    SENTRY_DSN: str = os.getenv("SENTRY_DSN", "")
    # 0.0 disables tracing; set to 0.1 or similar if you want performance traces.
    SENTRY_TRACES_SAMPLE_RATE: float = float(os.getenv("SENTRY_TRACES_SAMPLE_RATE", "0.0"))

    @classmethod
    def validate(cls):
        # Check if keys are non-empty AND not placeholders
        def is_placeholder(key):
            return not key or "your-" in key.lower() or "sk-" == key or "nvapi-" == key

        if is_placeholder(cls.OPENAI_API_KEY):
            logger.warning("OPENAI_API_KEY is missing or using a placeholder!")
        
        # Mask keys for logging
        def mask(key: str): return f"{key[:8]}...{key[-4:]}" if len(key) > 8 else "****"
        
        logger.info("Config status:")
        logger.info(f"  - OpenAI Model: {cls.OPENAI_MODEL}")
        logger.info(f"  - Vector Store: {cls.VECTOR_STORE_TYPE}")
        
        if not is_placeholder(cls.NVIDIA_API_KEY):
            logger.info(f"  - NVIDIA Engine: {cls.NVIDIA_MODEL} (Key: {mask(cls.NVIDIA_API_KEY)})")
        else:
            logger.info("  - NVIDIA Engine: INACTIVE (Missing API Key)")

        if is_placeholder(cls.OPENAI_API_KEY):
            logger.info("  - OpenAI Status: INACTIVE (Missing API Key)")
        else:
            logger.info("  - OpenAI Status: ACTIVE")

config = Config()
