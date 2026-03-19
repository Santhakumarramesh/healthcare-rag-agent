"""
Session-scoped personal document store for the Medical Record Summarizer.

Documents live only in-memory for the duration of a user session and are
never written to disk — keeping uploaded health records private.
"""
import io
import threading
import sys
from pathlib import Path
from dataclasses import dataclass, field

import faiss
import numpy as np
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from loguru import logger

sys.path.append(str(Path(__file__).parent.parent))
from utils.config import config


@dataclass
class PersonalChunk:
    text: str
    metadata: dict
    score: float = 0.0


class _SessionStore:
    """Per-session in-memory FAISS index + raw text storage."""

    EMBEDDING_DIM = 1536  # text-embedding-3-small

    def __init__(self):
        self.index: faiss.Index = faiss.IndexFlatIP(self.EMBEDDING_DIM)
        self.chunks: list[dict] = []
        self.full_texts: dict[str, str] = {}   # filename -> raw extracted text
        self.files: list[str] = []


class PersonalDocumentStore:
    """
    Singleton that manages one _SessionStore per session_id.
    Uses OpenAI text-embedding-3-small (1536-dim) for embeddings so it
    matches what ingest.py uses in production — no sentence-transformers needed.
    """

    def __init__(self):
        self._sessions: dict[str, _SessionStore] = {}
        self._lock = threading.Lock()
        self._embedder = OpenAIEmbeddings(
            model="text-embedding-3-small",
            openai_api_key=config.OPENAI_API_KEY,
        )
        self._splitter = RecursiveCharacterTextSplitter(
            chunk_size=400,
            chunk_overlap=50,
            separators=["\n\n", "\n", ". ", " ", ""],
        )
        logger.info("PersonalDocumentStore initialized.")

    # ── Internal helpers ───────────────────────────────────────────────────────

    def _get_or_create(self, session_id: str) -> _SessionStore:
        if session_id not in self._sessions:
            self._sessions[session_id] = _SessionStore()
        return self._sessions[session_id]

    def _embed_and_add(self, store: _SessionStore, chunks: list[dict]):
        texts = [c["text"] for c in chunks]
        embeddings = self._embedder.embed_documents(texts)
        vecs = np.array(embeddings, dtype="float32")
        # Normalize → cosine similarity via inner product
        norms = np.linalg.norm(vecs, axis=1, keepdims=True)
        vecs = vecs / np.where(norms > 0, norms, 1.0)
        store.index.add(vecs)
        store.chunks.extend(chunks)

    # ── Public API ─────────────────────────────────────────────────────────────

    def add_pdf(self, session_id: str, pdf_bytes: bytes, filename: str) -> int:
        """
        Extract text from a PDF using multiple strategies:
        1. Try pypdf for text-based PDFs
        2. Fall back to OCR for scanned/image-based PDFs
        3. Use pdfplumber for better table extraction
        """
        import pdfplumber
        from pypdf import PdfReader
        
        full_text = ""
        
        # Strategy 1: Try pdfplumber first (better for tables and layouts)
        try:
            with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
                pages_text = []
                for page in pdf.pages:
                    # Extract text
                    text = page.extract_text()
                    
                    # Extract tables separately
                    tables = page.extract_tables()
                    if tables:
                        for table in tables:
                            # Convert table to readable text format
                            table_text = "\n".join([
                                " | ".join([str(cell) if cell else "" for cell in row])
                                for row in table if row
                            ])
                            text = (text or "") + "\n\nTable:\n" + table_text
                    
                    if text and text.strip():
                        pages_text.append(text)
                
                if pages_text:
                    full_text = "\n\n=== PAGE BREAK ===\n\n".join(pages_text)
                    logger.info(f"[PersonalStore] Extracted {len(pages_text)} pages using pdfplumber")
        except Exception as e:
            logger.warning(f"[PersonalStore] pdfplumber failed: {e}, trying pypdf...")
        
        # Strategy 2: Fall back to pypdf if pdfplumber failed
        if not full_text:
            try:
                reader = PdfReader(io.BytesIO(pdf_bytes))
                pages = []
                for p in reader.pages:
                    text = p.extract_text()
                    if text and text.strip():
                        pages.append(text)
                
                if pages:
                    full_text = "\n\n=== PAGE BREAK ===\n\n".join(pages)
                    logger.info(f"[PersonalStore] Extracted {len(pages)} pages using pypdf")
            except Exception as e:
                logger.warning(f"[PersonalStore] pypdf failed: {e}")
        
        # Strategy 3: Try OCR for image-based PDFs (scanned documents) - OPTIONAL
        if not full_text or len(full_text.strip()) < 100:
            try:
                import pytesseract
                from pdf2image import convert_from_bytes
                
                logger.info("[PersonalStore] Attempting OCR extraction...")
                images = convert_from_bytes(pdf_bytes, dpi=300, fmt='png')
                ocr_pages = []
                
                for i, img in enumerate(images):
                    # Use pytesseract for OCR
                    text = pytesseract.image_to_string(img, lang='eng', config='--psm 6')
                    if text and text.strip():
                        ocr_pages.append(f"[Page {i+1} - OCR]\n{text}")
                
                if ocr_pages:
                    full_text = "\n\n=== PAGE BREAK ===\n\n".join(ocr_pages)
                    logger.info(f"[PersonalStore] Extracted {len(ocr_pages)} pages using OCR")
            except ImportError as e:
                logger.warning(f"[PersonalStore] OCR not available: {e}. Install tesseract-ocr for scanned PDF support.")
            except Exception as e:
                logger.warning(f"[PersonalStore] OCR extraction failed: {e}. Document may be image-based.")
        
        # Final check
        if not full_text or len(full_text.strip()) < 50:
            raise ValueError(
                f"Could not extract meaningful text from '{filename}'. "
                "The PDF may be encrypted, corrupted, or contain only images without OCR support."
            )
        
        logger.info(f"[PersonalStore] Final extracted text length: {len(full_text)} chars")
        return self._add_text_internal(session_id, full_text, filename)

    def add_text(self, session_id: str, text: str, filename: str) -> int:
        """Chunk and embed plain text, store in the session."""
        if not text.strip():
            raise ValueError(f"'{filename}' appears to be empty.")
        return self._add_text_internal(session_id, text, filename)

    def _add_text_internal(self, session_id: str, full_text: str, filename: str) -> int:
        chunk_texts = self._splitter.split_text(full_text)
        chunks = [
            {
                "text": t,
                "metadata": {
                    "source": filename,
                    "chunk_index": i,
                    "total_chunks": len(chunk_texts),
                },
            }
            for i, t in enumerate(chunk_texts)
        ]
        with self._lock:
            store = self._get_or_create(session_id)
            self._embed_and_add(store, chunks)
            store.full_texts[filename] = full_text
            if filename not in store.files:
                store.files.append(filename)
        logger.info(
            f"[PersonalStore] session={session_id[:8]} | +{len(chunks)} chunks from '{filename}'"
        )
        return len(chunks)

    def query(self, session_id: str, query: str, top_k: int = 5) -> list[PersonalChunk]:
        """Return the top-k chunks most relevant to the query."""
        with self._lock:
            store = self._sessions.get(session_id)
        if not store or store.index.ntotal == 0:
            return []

        q_emb = self._embedder.embed_query(query)
        q_vec = np.array([q_emb], dtype="float32")
        q_vec /= np.linalg.norm(q_vec) + 1e-9

        k = min(top_k, store.index.ntotal)
        scores, indices = store.index.search(q_vec, k)

        results: list[PersonalChunk] = []
        for score, idx in zip(scores[0], indices[0]):
            if idx == -1:
                continue
            chunk = store.chunks[idx]
            results.append(PersonalChunk(
                text=chunk["text"],
                metadata=chunk["metadata"],
                score=float(score),
            ))
        return results

    def get_full_text(self, session_id: str) -> str:
        """Return the concatenated raw text of all uploaded files (for extraction)."""
        with self._lock:
            store = self._sessions.get(session_id)
        if not store:
            return ""
        return "\n\n===== NEXT DOCUMENT =====\n\n".join(store.full_texts.values())

    def list_files(self, session_id: str) -> list[str]:
        with self._lock:
            store = self._sessions.get(session_id)
        return list(store.files) if store else []

    def chunk_count(self, session_id: str) -> int:
        with self._lock:
            store = self._sessions.get(session_id)
        return store.index.ntotal if store else 0

    def clear(self, session_id: str):
        with self._lock:
            self._sessions.pop(session_id, None)
        logger.info(f"[PersonalStore] Cleared session {session_id[:8]}")


# Singleton — shared across all FastAPI workers in-process
personal_store = PersonalDocumentStore()
