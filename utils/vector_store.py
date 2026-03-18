"""
utils/vector_store.py
---------------------
Hybrid FAISS + Pinecone vector store with semantic re-ranking.
Supports ingesting PDFs, text files, and raw strings.
"""

import os
import hashlib
from pathlib import Path
from typing import List, Optional, Dict, Any

import faiss
import numpy as np
from loguru import logger
from dotenv import load_dotenv

from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import PyPDFLoader, TextLoader, DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document

load_dotenv()

# ── Config ────────────────────────────────────────────────────────────────────
from config import get_settings

settings = get_settings()
VECTOR_STORE_MODE = settings.vector_store_mode
FAISS_INDEX_PATH  = settings.faiss_index_path
CHUNK_SIZE        = 512
CHUNK_OVERLAP     = 64
TOP_K_RETRIEVE    = 8
TOP_K_RERANK      = 4


class HybridVectorStore:
    """
    Wraps FAISS (local, fast) and optionally Pinecone (scalable, persistent).
    Re-ranks results using a cross-encoder-style cosine scoring step.
    """

    def __init__(self):
        self.embeddings = OpenAIEmbeddings(
            model="text-embedding-3-small",
            openai_api_key=os.getenv("OPENAI_API_KEY"),
        )
        self.faiss_store: Optional[FAISS] = None
        self.pinecone_store = None
        self._splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP,
            separators=["\n\n", "\n", ".", "!", "?", ",", " "],
        )
        self._load_or_create_faiss()

    # ── FAISS ─────────────────────────────────────────────────────────────────

    def _load_or_create_faiss(self):
        if Path(FAISS_INDEX_PATH).exists():
            logger.info("Loading existing FAISS index from disk...")
            self.faiss_store = FAISS.load_local(
                FAISS_INDEX_PATH,
                self.embeddings,
                allow_dangerous_deserialization=True,
            )
            logger.info("FAISS index loaded.")
        else:
            logger.info("No FAISS index found — will create on first ingest.")

    def _save_faiss(self):
        Path(FAISS_INDEX_PATH).mkdir(parents=True, exist_ok=True)
        self.faiss_store.save_local(FAISS_INDEX_PATH)
        logger.info(f"FAISS index saved to {FAISS_INDEX_PATH}")

    # ── Pinecone (optional) ───────────────────────────────────────────────────

    def _init_pinecone(self):
        try:
            from pinecone import Pinecone, ServerlessSpec
            from langchain_community.vectorstores import Pinecone as LangchainPinecone

            pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
            index_name = os.getenv("PINECONE_INDEX_NAME", "healthcare-rag")

            if index_name not in [i.name for i in pc.list_indexes()]:
                pc.create_index(
                    name=index_name,
                    dimension=1536,
                    metric="cosine",
                    spec=ServerlessSpec(cloud="aws", region="us-east-1"),
                )
                logger.info(f"Created Pinecone index: {index_name}")

            self.pinecone_store = LangchainPinecone.from_existing_index(
                index_name=index_name,
                embedding=self.embeddings,
            )
            logger.info("Pinecone initialized.")
        except Exception as e:
            logger.warning(f"Pinecone init failed (will use FAISS only): {e}")

    # ── Ingestion ─────────────────────────────────────────────────────────────

    def ingest_documents(self, source: str) -> int:
        """
        Ingest a file path, directory, or raw text string.
        Returns number of chunks stored.
        """
        docs = self._load_source(source)
        chunks = self._splitter.split_documents(docs)
        self._add_metadata(chunks, source)

        logger.info(f"Ingesting {len(chunks)} chunks from: {source}")

        if self.faiss_store is None:
            self.faiss_store = FAISS.from_documents(chunks, self.embeddings)
        else:
            self.faiss_store.add_documents(chunks)

        self._save_faiss()

        if VECTOR_STORE_MODE in ("pinecone", "hybrid"):
            if self.pinecone_store is None:
                self._init_pinecone()
            if self.pinecone_store:
                self.pinecone_store.add_documents(chunks)

        return len(chunks)

    def ingest_text(self, text: str, source_name: str = "manual") -> int:
        """Ingest raw text directly."""
        doc = Document(page_content=text, metadata={"source": source_name})
        return self.ingest_documents_list([doc])

    def ingest_documents_list(self, docs: List[Document]) -> int:
        chunks = self._splitter.split_documents(docs)
        if self.faiss_store is None:
            self.faiss_store = FAISS.from_documents(chunks, self.embeddings)
        else:
            self.faiss_store.add_documents(chunks)
        self._save_faiss()
        return len(chunks)

    def _load_source(self, source: str) -> List[Document]:
        path = Path(source)
        if path.is_dir():
            loader = DirectoryLoader(source, glob="**/*.pdf", loader_cls=PyPDFLoader)
            return loader.load()
        elif source.endswith(".pdf"):
            return PyPDFLoader(source).load()
        elif source.endswith(".txt") or source.endswith(".md"):
            return TextLoader(source).load()
        else:
            return [Document(page_content=source, metadata={"source": "inline"})]

    def _add_metadata(self, chunks: List[Document], source: str):
        for i, chunk in enumerate(chunks):
            chunk.metadata.update({
                "chunk_id": hashlib.md5(chunk.page_content.encode()).hexdigest()[:8],
                "chunk_index": i,
                "domain": "healthcare",
            })

    # ── Retrieval ─────────────────────────────────────────────────────────────

    def retrieve(self, query: str, top_k: int = TOP_K_RETRIEVE) -> List[Document]:
        """
        Retrieve from FAISS (and Pinecone in hybrid mode),
        then re-rank by cosine similarity to return top_k results.
        """
        if self.faiss_store is None:
            logger.warning("Vector store is empty — no documents ingested yet.")
            return []

        faiss_results = self.faiss_store.similarity_search_with_score(query, k=top_k)
        candidates = [(doc, score) for doc, score in faiss_results]

        if VECTOR_STORE_MODE == "hybrid" and self.pinecone_store:
            pinecone_results = self.pinecone_store.similarity_search(query, k=top_k // 2)
            for doc in pinecone_results:
                # Avoid duplicates
                if not any(doc.page_content == c.page_content for c, _ in candidates):
                    candidates.append((doc, 0.5))

        reranked = self._rerank(query, candidates, top_k=TOP_K_RERANK)
        return reranked

    def _rerank(
        self,
        query: str,
        candidates: List[tuple],
        top_k: int = TOP_K_RERANK,
    ) -> List[Document]:
        """
        Re-rank candidates using embedding cosine similarity.
        FAISS scores are L2 distances — convert to similarity.
        """
        if not candidates:
            return []

        query_emb = np.array(self.embeddings.embed_query(query))

        scored = []
        for doc, raw_score in candidates:
            doc_emb = np.array(self.embeddings.embed_query(doc.page_content))
            cosine = float(
                np.dot(query_emb, doc_emb)
                / (np.linalg.norm(query_emb) * np.linalg.norm(doc_emb) + 1e-8)
            )
            doc.metadata["rerank_score"] = round(cosine, 4)
            scored.append((doc, cosine))

        scored.sort(key=lambda x: x[1], reverse=True)
        return [doc for doc, _ in scored[:top_k]]

    def get_stats(self) -> Dict[str, Any]:
        stats = {"mode": VECTOR_STORE_MODE}
        if self.faiss_store:
            stats["faiss_vectors"] = self.faiss_store.index.ntotal
        if self.pinecone_store:
            stats["pinecone_connected"] = True
        return stats
