"""
Document ingestion pipeline.
Supports: raw text, PDF files → chunked → embedded → FAISS index.
"""
import os
import sys
import pickle
from pathlib import Path
from typing import Optional

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from langchain.text_splitter import RecursiveCharacterTextSplitter
from loguru import logger

sys.path.append(str(Path(__file__).parent.parent))
from utils.config import config
from data.sample_medical_faq import get_documents_as_text


class DocumentIngestionPipeline:
    """
    End-to-end ingestion pipeline:
    Raw Documents → Chunking → Embedding → FAISS Index
    """

    def __init__(self):
        logger.info(f"Loading embedding model: {config.EMBEDDING_MODEL}")
        self.embedder = SentenceTransformer(config.EMBEDDING_MODEL)
        self.embedding_dim = self.embedder.get_sentence_embedding_dimension()
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=512,
            chunk_overlap=64,
            separators=["\n\n", "\n", ". ", " ", ""],
        )
        self.index_path = Path(config.FAISS_INDEX_PATH)
        self.index_path.mkdir(parents=True, exist_ok=True)
        logger.info(f"Embedding dim: {self.embedding_dim} | Index path: {self.index_path}")

    def chunk_documents(self, documents: list) -> list:
        """Split documents into overlapping chunks for better retrieval."""
        chunks = []
        for doc in documents:
            text_chunks = self.text_splitter.split_text(doc["text"])
            for i, chunk in enumerate(text_chunks):
                chunks.append({
                    "text": chunk,
                    "metadata": {
                        **doc["metadata"],
                        "chunk_id": f"{doc['metadata']['id']}_chunk_{i}",
                        "chunk_index": i,
                        "total_chunks": len(text_chunks),
                    }
                })
        logger.info(f"Chunked {len(documents)} documents -> {len(chunks)} chunks")
        return chunks

    def embed_chunks(self, chunks: list) -> np.ndarray:
        """Generate embeddings for all chunks using SentenceTransformers."""
        texts = [c["text"] for c in chunks]
        logger.info(f"Embedding {len(texts)} chunks...")
        embeddings = self.embedder.encode(
            texts,
            batch_size=32,
            show_progress_bar=True,
            normalize_embeddings=True,
        )
        return embeddings.astype("float32")

    def build_faiss_index(self, embeddings: np.ndarray) -> faiss.Index:
        """Build FAISS IndexFlatIP (inner product = cosine for normalized vectors)."""
        index = faiss.IndexFlatIP(self.embedding_dim)
        index.add(embeddings)
        logger.info(f"FAISS index built with {index.ntotal} vectors")
        return index

    def save_index(self, index: faiss.Index, chunks: list):
        """Persist FAISS index and chunk metadata to disk."""
        faiss.write_index(index, str(self.index_path / "index.faiss"))
        with open(self.index_path / "chunks.pkl", "wb") as f:
            pickle.dump(chunks, f)
        logger.success(f"Index saved to {self.index_path}")

    def load_index(self):
        """Load existing FAISS index and metadata from disk."""
        index = faiss.read_index(str(self.index_path / "index.faiss"))
        with open(self.index_path / "chunks.pkl", "rb") as f:
            chunks = pickle.load(f)
        logger.info(f"Loaded FAISS index: {index.ntotal} vectors, {len(chunks)} chunks")
        return index, chunks

    def index_exists(self) -> bool:
        return (
            (self.index_path / "index.faiss").exists() and
            (self.index_path / "chunks.pkl").exists()
        )

    def ingest_pdf(self, pdf_path: str) -> list:
        """Ingest a PDF file and return document dicts."""
        from pypdf import PdfReader
        reader = PdfReader(pdf_path)
        documents = []
        for i, page in enumerate(reader.pages):
            text = page.extract_text()
            if text.strip():
                documents.append({
                    "text": text,
                    "metadata": {
                        "id": f"pdf_{Path(pdf_path).stem}_p{i}",
                        "category": "PDF Document",
                        "question": f"Content from {Path(pdf_path).name} page {i+1}",
                        "source": pdf_path,
                    }
                })
        logger.info(f"Extracted {len(documents)} pages from {pdf_path}")
        return documents

    def run(self, extra_pdf_paths: Optional[list] = None, force_rebuild: bool = False):
        """Main ingestion pipeline runner."""
        if self.index_exists() and not force_rebuild:
            logger.info("Index already exists. Use force_rebuild=True to rebuild.")
            return self.load_index()

        documents = get_documents_as_text()
        logger.info(f"Loaded {len(documents)} base FAQ documents")

        if extra_pdf_paths:
            for pdf_path in extra_pdf_paths:
                if os.path.exists(pdf_path):
                    documents.extend(self.ingest_pdf(pdf_path))

        chunks = self.chunk_documents(documents)
        embeddings = self.embed_chunks(chunks)
        index = self.build_faiss_index(embeddings)
        self.save_index(index, chunks)

        return index, chunks


if __name__ == "__main__":
    import os
    pipeline = DocumentIngestionPipeline()

    # Also ingest the curated healthcare knowledge base if it exists
    kb_path = Path(__file__).parent.parent / "data" / "healthcare_knowledge_base.md"
    extra = [str(kb_path)] if kb_path.exists() else []

    pipeline.run(extra_pdf_paths=extra, force_rebuild=True)
    logger.success(f"Ingestion complete! Index at: {pipeline.index_path}")
