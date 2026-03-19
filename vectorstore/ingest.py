"""
Document ingestion pipeline.
Supports: raw text, PDF files → chunked → embedded → FAISS index.
Uses OpenAI embeddings on Render (no torch/sentence-transformers needed).
Falls back to SentenceTransformer locally.
"""
import os
import sys
import pickle
from pathlib import Path
from typing import Optional

import faiss
import numpy as np
from langchain_text_splitters import RecursiveCharacterTextSplitter
from loguru import logger

sys.path.append(str(Path(__file__).parent.parent))
from utils.config import config
from data.sample_medical_faq import get_documents_as_text


def _get_embedder():
    """
    Use OpenAI embeddings in production (lightweight, no torch).
    Fall back to SentenceTransformer locally when no API key is set.
    """
    key = (config.OPENAI_API_KEY or "").strip()
    # A real OpenAI key is >40 chars and is NOT a known placeholder string
    PLACEHOLDERS = {"sk-your-key-here", "sk-placeholder", "your-key-here", ""}
    has_real_key = len(key) > 30 and key not in PLACEHOLDERS

    if has_real_key:
        from langchain_openai import OpenAIEmbeddings
        logger.info("Using OpenAI embeddings (text-embedding-3-small)")
        return OpenAIEmbeddings(
            model="text-embedding-3-small",
            openai_api_key=key,
        ), 1536

    # Fallback: SentenceTransformer (local, no API key needed)
    try:
        from sentence_transformers import SentenceTransformer
        logger.info(f"OpenAI key not set — using SentenceTransformer: {config.EMBEDDING_MODEL}")
        model = SentenceTransformer(config.EMBEDDING_MODEL)
        return model, model.get_sentence_embedding_dimension()
    except ImportError:
        raise RuntimeError(
            "No embedder available. Either set OPENAI_API_KEY or "
            "run: pip install sentence-transformers"
        )


class DocumentIngestionPipeline:
    """
    End-to-end ingestion pipeline:
    Raw Documents → Chunking → Embedding → FAISS Index
    """

    def __init__(self):
        self.embedder, self.embedding_dim = _get_embedder()
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=512,
            chunk_overlap=64,
            separators=["\n\n", "\n", ". ", " ", ""],
        )
        self.index_path = Path(config.FAISS_INDEX_PATH)
        self.index_path.mkdir(parents=True, exist_ok=True)
        logger.info(f"Embedding dim: {self.embedding_dim} | Index path: {self.index_path}")

    def embed_texts(self, texts: list) -> np.ndarray:
        """Embed texts using OpenAI or SentenceTransformer depending on environment."""
        logger.info(f"Embedding {len(texts)} chunks...")
        from langchain_openai import OpenAIEmbeddings
        if isinstance(self.embedder, OpenAIEmbeddings):
            # OpenAI batch embedding
            embeddings = self.embedder.embed_documents(texts)
            return np.array(embeddings, dtype="float32")
        else:
            # SentenceTransformer local
            embeddings = self.embedder.encode(
                texts, batch_size=32, show_progress_bar=True, normalize_embeddings=True
            )
            return embeddings.astype("float32")

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

    def build_faiss_index(self, embeddings: np.ndarray) -> faiss.Index:
        """Build FAISS IndexFlatIP (inner product = cosine for normalized vectors)."""
        index = faiss.IndexFlatIP(self.embedding_dim)
        index.add(embeddings)
        logger.info(f"FAISS index built with {index.ntotal} vectors")
        return index

    def save_index(self, index: faiss.Index, chunks: list):
        faiss.write_index(index, str(self.index_path / "index.faiss"))
        with open(self.index_path / "chunks.pkl", "wb") as f:
            pickle.dump(chunks, f)
        logger.success(f"Index saved to {self.index_path}")

    def load_index(self):
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
        return documents

    def _add_documents_to_index(self, docs: list) -> int:
        """Add LangChain Document objects to the existing FAISS index."""
        from langchain.schema import Document
        texts = [d.page_content for d in docs]
        chunks = [{"text": t, "metadata": getattr(d, "metadata", {})} for d, t in zip(docs, texts)]
        embeddings = self.embed_texts(texts)
        if self.index_exists():
            idx, existing = self.load_index()
            import numpy as np
            idx.add(embeddings)
            combined = existing + chunks
            self.save_index(idx, combined)
        else:
            index = self.build_faiss_index(embeddings)
            self.save_index(index, chunks)
        return len(chunks)

    def _ingest_file_to_index(self, file_path: str, source_name: str = "") -> int:
        """Ingest a single file (PDF or text) into the shared index."""
        suffix = Path(file_path).suffix.lower()
        if suffix == ".pdf":
            docs = self.ingest_pdf(file_path)
        else:
            docs = self._ingest_text_file(file_path)
        all_chunks = self.chunk_documents(docs)
        texts = [c["text"] for c in all_chunks]
        embeddings = self.embed_texts(texts)
        if self.index_exists():
            idx, existing = self.load_index()
            idx.add(embeddings)
            self.save_index(idx, existing + all_chunks)
        else:
            index = self.build_faiss_index(embeddings)
            self.save_index(index, all_chunks)
        return len(all_chunks)

    def run(self, extra_paths: Optional[list] = None, force_rebuild: bool = False,
            # kept for backward compat
            extra_pdf_paths: Optional[list] = None):
        """
        Main ingestion runner.
        Accepts extra_paths (any file type) or extra_pdf_paths (legacy name).
        """
        all_extra = list(extra_paths or []) + list(extra_pdf_paths or [])

        if self.index_exists() and not force_rebuild:
            logger.info("Index already exists.")
            return self.load_index()

        documents = get_documents_as_text()
        logger.info(f"Loaded {len(documents)} base FAQ documents")

        for path in all_extra:
            if not os.path.exists(path):
                continue
            suffix = Path(path).suffix.lower()
            if suffix == ".pdf":
                documents.extend(self.ingest_pdf(path))
            elif suffix in (".txt", ".md", ".text"):
                documents.extend(self._ingest_text_file(path))
            else:
                logger.warning(f"Skipping unsupported file type: {path}")

        chunks = self.chunk_documents(documents)
        texts = [c["text"] for c in chunks]
        embeddings = self.embed_texts(texts)
        index = self.build_faiss_index(embeddings)
        self.save_index(index, chunks)
        return index, chunks

    def _ingest_text_file(self, file_path: str) -> list:
        """Ingest a plain-text or markdown file."""
        text = Path(file_path).read_text(encoding="utf-8", errors="replace")
        name = Path(file_path).name
        return [{
            "text": text,
            "metadata": {
                "id": f"txt_{Path(file_path).stem}",
                "category": "Knowledge Base",
                "question": f"Content from {name}",
                "source": file_path,
            }
        }]


if __name__ == "__main__":
    pipeline = DocumentIngestionPipeline()
    # No local knowledge base — rely on OpenAI's knowledge + user-uploaded documents only
    pipeline.run(extra_paths=[], force_rebuild=True)
    logger.success(f"Ingestion complete! Index at: {pipeline.index_path}")
