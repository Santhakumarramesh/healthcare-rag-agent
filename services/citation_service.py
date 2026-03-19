"""
Citation Service - Formats and manages source citations.

Provides structured citations for retrieved documents.
"""
from typing import List, Dict
from loguru import logger


class CitationService:
    """Formats citations from retrieved documents"""
    
    @staticmethod
    def format_citations(sources: List, max_sources: int = 5) -> List[Dict]:
        """
        Format retrieved documents as citations.
        
        Args:
            sources: List of retrieved documents with metadata
            max_sources: Maximum number of citations to return
        
        Returns:
            List of formatted citation dictionaries
        """
        citations = []
        
        for i, doc in enumerate(sources[:max_sources], 1):
            # Extract metadata
            metadata = getattr(doc, 'metadata', {})
            
            # Get source information
            source_name = metadata.get('source', 'Medical Knowledge Base')
            category = metadata.get('category', 'General')
            url = metadata.get('url', '#')
            
            # Get relevance score
            score = getattr(doc, 'score', 0.0)
            if hasattr(doc, 'relevance_score'):
                score = doc.relevance_score
            
            # Get content excerpt
            content = getattr(doc, 'page_content', '')
            if hasattr(doc, 'text'):
                content = doc.text
            
            excerpt = content[:300] + "..." if len(content) > 300 else content
            
            citation = {
                "id": i,
                "title": source_name,
                "category": category,
                "url": url,
                "relevance_score": round(float(score), 3),
                "excerpt": excerpt,
                "full_content": content
            }
            
            citations.append(citation)
        
        logger.debug(f"[CitationService] Formatted {len(citations)} citations")
        return citations
    
    @staticmethod
    def format_citation_text(citations: List[Dict]) -> str:
        """
        Format citations as readable text.
        
        Args:
            citations: List of citation dictionaries
        
        Returns:
            Formatted citation text
        """
        if not citations:
            return "No sources available."
        
        citation_parts = ["Sources:"]
        for citation in citations:
            citation_parts.append(
                f"\n[{citation['id']}] {citation['title']} "
                f"(Relevance: {citation['relevance_score']*100:.0f}%)"
            )
        
        return "\n".join(citation_parts)
    
    @staticmethod
    def get_citation_summary(citations: List[Dict]) -> Dict:
        """
        Get summary statistics for citations.
        
        Args:
            citations: List of citation dictionaries
        
        Returns:
            Summary statistics
        """
        if not citations:
            return {
                "count": 0,
                "avg_relevance": 0.0,
                "categories": []
            }
        
        avg_relevance = sum(c['relevance_score'] for c in citations) / len(citations)
        categories = list(set(c['category'] for c in citations))
        
        return {
            "count": len(citations),
            "avg_relevance": round(avg_relevance, 3),
            "categories": categories,
            "top_source": citations[0]['title'] if citations else None
        }


# Singleton instance
citation_service = CitationService()
