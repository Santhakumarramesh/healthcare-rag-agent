import pytest
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.config import config


def test_settings_load_defaults():
    """Test that the application config loads proper defaults."""
    assert config.VECTOR_STORE_TYPE in ["faiss", "pinecone"]
    assert config.FAISS_INDEX_PATH is not None


def test_chunk_parameters():
    """Test that retrieval config values are valid."""
    assert config.MAX_RETRIEVED_DOCS > 0
    assert config.RERANK_TOP_K > 0
    assert config.MAX_RETRIEVED_DOCS >= config.RERANK_TOP_K


def test_api_port_config():
    """Test API host and port configuration validity."""
    assert isinstance(config.API_PORT, int)
    assert config.API_PORT > 0
    assert isinstance(config.API_HOST, str)
