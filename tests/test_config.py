import pytest
import os
import sys

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.config import config

def test_settings_load_defaults():
    """Test that the application config loads proper defaults."""
    settings = get_settings()
    assert settings.vector_store_mode in ["faiss", "pinecone"]
    assert settings.faiss_index_path is not None

def test_chunk_parameters():
    """Test that text chunking configurations are musically valid."""
    settings = get_settings()
    assert settings.chunk_size > 0
    assert settings.chunk_overlap > 0
    assert settings.chunk_size > settings.chunk_overlap

def test_api_port_config():
    """Test API host and port configuration validity."""
    settings = get_settings()
    assert isinstance(settings.api_port, int)
    assert settings.api_port == 8000  # Default port
    assert isinstance(settings.api_host, str)
