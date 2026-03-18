"""
data/ingest_knowledge_base.py
------------------------------
Run this ONCE after setup to populate the vector store
with the healthcare knowledge base.

Usage:
    python data/ingest_knowledge_base.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pathlib import Path
from loguru import logger
from dotenv import load_dotenv

load_dotenv()


def main():
    logger.info("=" * 60)
    logger.info("Healthcare RAG — Knowledge Base Ingestion")
    logger.info("=" * 60)

    from utils.vector_store import HybridVectorStore
    vs = HybridVectorStore()

    kb_path = Path(__file__).parent / "healthcare_knowledge_base.md"

    if not kb_path.exists():
        logger.error(f"Knowledge base file not found: {kb_path}")
        sys.exit(1)

    logger.info(f"Ingesting: {kb_path}")
    chunks = vs.ingest_documents(str(kb_path))
    logger.info(f"✅ Ingested {chunks} chunks into vector store.")

    # Quick test retrieval
    test_query = "What are the symptoms of diabetes?"
    logger.info(f"\nTest retrieval: '{test_query}'")
    results = vs.retrieve(test_query, top_k=2)

    if results:
        logger.info(f"✅ Retrieved {len(results)} documents:")
        for i, doc in enumerate(results):
            score = doc.metadata.get("rerank_score", "N/A")
            logger.info(f"  [{i+1}] Score={score} | {doc.page_content[:100]}...")
    else:
        logger.warning("⚠️ No results retrieved — check your OpenAI API key.")

    stats = vs.get_stats()
    logger.info(f"\nVector Store Stats: {stats}")
    logger.info("\n✅ Knowledge base ready! You can now start the API and Streamlit app.")


if __name__ == "__main__":
    main()
