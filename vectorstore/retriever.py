"""
Hybrid retriever: FAISS semantic search + cross-encoder reranking.
This is the core retrieval engine of the RAG pipeline.
"""
import sys
import pickle
from pathlib import Path
from dataclasses import dataclass

import faiss
import numpy as np
from loguru import logger
from pinecone import Pinecone
from rank_bm25 import BM25Okapi
import re

# sentence-transformers pulls torch (~2 GB) — not installed on Render.
# langchain-nvidia-ai-endpoints pulls CUDA packages — not installed on Render.
# Both are gracefully optional; OpenAI embeddings are used instead.
try:
    from sentence_transformers import SentenceTransformer, CrossEncoder
    _SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    _SENTENCE_TRANSFORMERS_AVAILABLE = False

try:
    from langchain_nvidia_ai_endpoints import NVIDIARerank
    _NVIDIA_RERANK_AVAILABLE = True
except ImportError:
    _NVIDIA_RERANK_AVAILABLE = False

sys.path.append(str(Path(__file__).parent.parent))
from utils.config import config


@dataclass
class RetrievedChunk:
    text: str
    metadata: dict
    score: float
    rerank_score: float = 0.0


class HybridRetriever:
    """
    Two-stage retrieval:
    Stage 1 — FAISS ANN search (fast, approximate, top-K candidates)
    Stage 2 — Cross-encoder reranking (precise, slower, top-N final results)
    """

    def __init__(self):
        logger.info("Initializing HybridRetriever...")
        self._init_embedder()
        self._init_reranker()

        self.index = None
        self.chunks = None
        self.pinecone_index = None
        self.bm25 = None

        try:
            self._load_index()
        except FileNotFoundError as e:
            logger.warning(f"Local FAISS index failed: {e}")
            if config.PINECONE_API_KEY:
                self._load_pinecone()
            else:
                logger.error("No vector store available (FAISS missing and Pinecone not configured).")

        logger.success("HybridRetriever ready.")

    def _init_embedder(self):
        """
        Use OpenAI embeddings when OPENAI_API_KEY is set (matches ingest.py logic).
        Fall back to SentenceTransformer locally when no API key is configured.
        This must stay consistent with ingest.py's _get_embedder() to avoid dimension mismatches.
        """
        key = (config.OPENAI_API_KEY or "").strip()
        PLACEHOLDERS = {"sk-your-key-here", "sk-placeholder", "your-key-here", ""}
        has_real_key = len(key) > 30 and key not in PLACEHOLDERS

        if has_real_key:
            from langchain_openai import OpenAIEmbeddings
            logger.info("Using OpenAI embeddings (text-embedding-3-small)")
            self._openai_embedder = OpenAIEmbeddings(
                model="text-embedding-3-small",
                openai_api_key=config.OPENAI_API_KEY,
            )
            self._embedding_dim = 1536
            self._use_openai = True
            self.embedder = None
        elif _SENTENCE_TRANSFORMERS_AVAILABLE:
            logger.info(f"Using SentenceTransformer: {config.EMBEDDING_MODEL}")
            self.embedder = SentenceTransformer(config.EMBEDDING_MODEL)
            self._embedding_dim = self.embedder.get_sentence_embedding_dimension()
            self._use_openai = False
            self._openai_embedder = None
        else:
            raise RuntimeError(
                "No embedder available. Set OPENAI_API_KEY or install sentence-transformers."
            )

    def _init_reranker(self):
        """
        Use NVIDIA NIM reranker when key is set.
        Skip local CrossEncoder — it uses joblib multiprocessing which crashes
        uvicorn workers on Python 3.13 (semaphore leak). RRF scores from Stage 1
        are sufficient for production quality without a cross-encoder.
        """
        if _NVIDIA_RERANK_AVAILABLE and config.NVIDIA_API_KEY and config.NVIDIA_API_KEY not in ("nvapi-your-key-here", ""):
            logger.debug(f"Using NVIDIA Reranker: {config.NVIDIA_RERANK_MODEL}")
            self.nvidia_reranker = NVIDIARerank(
                model=config.NVIDIA_RERANK_MODEL,
                api_key=config.NVIDIA_API_KEY,
            )
            self.rerank_model = None
        else:
            # No reranker — return Stage 1 RRF results directly (stable, no crash)
            logger.info("Using RRF scores only (no cross-encoder reranker)")
            self.rerank_model = None
            self.nvidia_reranker = None

    def _load_pinecone(self):
        """Initialize Pinecone for cloud-hosted retrieval."""
        try:
            logger.info(f"Connecting to Pinecone index: {config.PINECONE_INDEX_NAME}...")
            pc = Pinecone(api_key=config.PINECONE_API_KEY)
            self.pinecone_index = pc.Index(config.PINECONE_INDEX_NAME)
            logger.success("Pinecone connection established.")
        except Exception as e:
            logger.error(f"Pinecone connection failed: {e}")

    def _load_index(self):
        index_path = Path(config.FAISS_INDEX_PATH)
        faiss_file = index_path / "index.faiss"
        chunks_file = index_path / "chunks.pkl"

        if not faiss_file.exists() or not chunks_file.exists():
            raise FileNotFoundError(
                f"FAISS index not found at {index_path}. "
                "Run: python vectorstore/ingest.py first."
            )

        self.index = faiss.read_index(str(faiss_file))
        with open(chunks_file, "rb") as f:
            self.chunks = pickle.load(f)

        if self.index:
            logger.info(f"Loaded {self.index.ntotal} vectors, {len(self.chunks)} chunks")
            # Initialize BM25 for keyword search
            tokenized_corpus = [self._tokenize(c["text"]) for c in self.chunks]
            self.bm25 = BM25Okapi(tokenized_corpus)
            logger.success("BM25 index initialized.")
        else:
            logger.warning("FAISS index not initialized.")

    def _tokenize(self, text: str) -> list:
        """Simple tokenizer for BM25."""
        return re.sub(r"[^\w\s]", "", text.lower()).split()

    def embed_query(self, query: str) -> np.ndarray:
        """Embed the user query using the same model as document embeddings."""
        if self._use_openai:
            embedding = self._openai_embedder.embed_query(query)
            return np.array([embedding], dtype="float32")
        else:
            embedding = self.embedder.encode(
                [query],
                normalize_embeddings=True,
                show_progress_bar=False,
            )
            return embedding.astype("float32")

    def faiss_search(self, query_embedding: np.ndarray, top_k: int) -> list:
        """Stage 1: Fast approximate nearest neighbor search (Local)."""
        if not self.index:
            return []
            
        scores, indices = self.index.search(query_embedding, top_k)
        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx == -1:
                continue
            results.append(RetrievedChunk(
                text=self.chunks[idx]["text"],
                metadata=self.chunks[idx]["metadata"],
                score=float(score),
            ))
        return results

    def bm25_search(self, query: str, top_k: int) -> list:
        """Stage 1: Keyword search via BM25."""
        if not self.bm25:
            return []
            
        tokenized_query = self._tokenize(query)
        scores = self.bm25.get_scores(tokenized_query)
        top_indices = np.argsort(scores)[::-1][:top_k]
        
        results = []
        for idx in top_indices:
            results.append(RetrievedChunk(
                text=self.chunks[idx]["text"],
                metadata=self.chunks[idx]["metadata"],
                score=float(scores[idx]),
            ))
        return results

    def reciprocal_rank_fusion(self, vector_results: list, keyword_results: list, k: int = 60) -> list:
        """Merge results from different retrievers using RRF."""
        fused_scores = {}
        # Track original objects by text to avoid complex metadata merging
        text_to_obj = {}
        
        for rank, res in enumerate(vector_results):
            text_to_obj[res.text] = res
            fused_scores[res.text] = fused_scores.get(res.text, 0) + 1.0 / (k + rank + 1)
            
        for rank, res in enumerate(keyword_results):
            text_to_obj[res.text] = res
            fused_scores[res.text] = fused_scores.get(res.text, 0) + 1.0 / (k + rank + 1)
            
        # Re-sort and take top candidates
        sorted_texts = sorted(fused_scores.items(), key=lambda x: x[1], reverse=True)
        
        final_results = []
        for text, score in sorted_texts:
            obj = text_to_obj[text]
            obj.score = score  # Overwrite with RRF score
            final_results.append(obj)
            
        return final_results

    def pinecone_search(self, query: str, top_k: int) -> list:
        """Stage 1: Vector search in the cloud (Pinecone)."""
        if not self.pinecone_index:
            return []

        if self._use_openai:
            embedding = self._openai_embedder.embed_query(query)
        else:
            embedding = self.embedder.encode(query).tolist()
        
        response = self.pinecone_index.query(
            vector=embedding,
            top_k=top_k,
            include_metadata=True
        )
        
        results = []
        for match in response["matches"]:
            metadata = match["metadata"]
            # Ensure 'text' exists in metadata (Pinecone standard for this app)
            text = metadata.get("text", metadata.get("content", ""))
            results.append(RetrievedChunk(
                text=text,
                metadata=metadata,
                score=float(match["score"])
            ))
        return results

    def rerank(self, query: str, chunks: list, top_k: int) -> list:
        """Stage 2: Rerank candidates using Cross-Encoder or NVIDIA NIM."""
        if not chunks:
            return []
            
        if self.nvidia_reranker:
            logger.info(f"Reranking {len(chunks)} chunks with NVIDIA NIM...")
            # NVIDIARerank expects docs as a list of strings or dicts
            texts = [c.text for c in chunks]
            
            try:
                # The NVIDIARerank.rerank method returns a list of Document objects
                # with relevance_score in metadata. We need to map this back to RetrievedChunk.
                reranked_docs = self.nvidia_reranker.rerank(query=query, documents=texts, top_n=top_k)
                
                # Create a mapping from original text to its chunk object
                text_to_chunk_map = {chunk.text: chunk for chunk in chunks}
                
                final_reranked_chunks = []
                for doc in reranked_docs:
                    original_chunk = text_to_chunk_map.get(doc.page_content)
                    if original_chunk:
                        original_chunk.rerank_score = doc.metadata.get("relevance_score", 0.0)
                        final_reranked_chunks.append(original_chunk)
                
                # Sort by rerank_score in descending order (NVIDIA reranker might not return them sorted)
                final_reranked_chunks.sort(key=lambda x: x.rerank_score, reverse=True)
                return final_reranked_chunks
                
            except Exception as e:
                logger.error(f"NVIDIA Rerank failed: {e}. Falling back to local reranker or top Stage 1 results.")
                # If NVIDIA reranker fails, try local if available, otherwise return top_k from stage 1
                if self.rerank_model:
                    logger.warning("Attempting local rerank due to NVIDIA failure.")
                    return self._local_rerank(query, chunks, top_k)
                else:
                    logger.warning("No local reranker available. Returning top Stage 1 results.")
                    return chunks[:top_k]

        # Local Cross-Encoder Rerank
        if self.rerank_model:
            return self._local_rerank(query, chunks, top_k)
            
        # Fallback if no reranker is configured or available
        logger.warning("No reranker configured or available. Returning top Stage 1 results without reranking.")
        return chunks[:top_k]

    def _local_rerank(self, query: str, chunks: list, top_k: int) -> list:
        """Helper for local Cross-Encoder reranking."""
        logger.info(f"Reranking {len(chunks)} chunks with Cross-Encoder...")
        sentence_pairs = [[query, chunk.text] for chunk in chunks]
        # n_jobs=1 disables joblib multiprocessing — prevents semaphore crash on Python 3.13 + uvicorn
        scores = self.rerank_model.predict(sentence_pairs, num_workers=0)
        
        for i, score in enumerate(scores):
            chunks[i].rerank_score = float(score)
            
        return sorted(chunks, key=lambda x: x.rerank_score, reverse=True)[:top_k]

    def retrieve(self, query: str, top_k: int = None, rerank_top_k: int = None) -> list:
        """
        Full two-stage retrieval pipeline.
        Returns top reranked chunks above confidence threshold.
        """
        top_k = top_k or config.MAX_RETRIEVED_DOCS
        rerank_top_k = rerank_top_k or config.RERANK_TOP_K

        logger.debug(f"Retrieving for query: '{query[:80]}...'")

        # Stage 1: Retrieval (Hybrid RRF or Pinecone)
        if self.index:
            query_embedding = self.embed_query(query)
            vector_candidates = self.faiss_search(query_embedding, top_k=top_k * 3)
            keyword_candidates = self.bm25_search(query, top_k=top_k * 3)
            
            candidates = self.reciprocal_rank_fusion(
                vector_candidates, 
                keyword_candidates, 
                k=config.RRF_K
            )
            logger.info(f"Hybrid RRF returned {len(candidates)} fused candidates")
        elif self.pinecone_index:
            candidates = self.pinecone_search(query, top_k=top_k * 2)
        else:
            logger.error("No active vector store for retrieval.")
            return []
            
        logger.debug(f"Stage 1 returned {len(candidates)} candidates")

        # Stage 2: Rerank
        reranked = self.rerank(query, candidates, top_k=rerank_top_k)
        final = reranked[:rerank_top_k]

        logger.debug(
            f"Reranked to {len(final)} results | "
            f"Top score: {final[0].rerank_score:.3f}" if final else "No results"
        )
        return final

    def format_context(self, chunks: list) -> str:
        """Format retrieved chunks into a single context string for the LLM."""
        if not chunks:
            return "No relevant information found in the knowledge base."

        context_parts = []
        for i, chunk in enumerate(chunks, 1):
            source = chunk.metadata.get("category", "Unknown")
            score = getattr(chunk, "rerank_score", 0.0)
            context_parts.append(
                f"[Source {i} | Category: {source} | Relevance: {score:.2f}]\n"
                f"{chunk.text}"
            )
        return "\n\n---\n\n".join(context_parts)
