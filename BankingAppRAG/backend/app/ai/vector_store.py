import json
import math
import re
from typing import List, Dict, Any, Tuple, Optional
from sqlalchemy.orm import Session
from app.models.rag import DocumentChunk, Document

def cosine_similarity(v1: List[float], v2: List[float]) -> float:
    """Computes cosine similarity between two float vectors"""
    if not v1 or not v2 or len(v1) != len(v2):
        return 0.0
    
    dot_product = sum(a * b for a, b in zip(v1, v2))
    norm_a = math.sqrt(sum(a * a for a, b in zip(v1, v2)))
    norm_b = math.sqrt(sum(b * b for a, b in zip(v1, v2)))
    
    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0
        
    return dot_product / (norm_a * norm_b)

def compute_keyword_score(query: str, text: str) -> float:
    """Computes normalized keyword overlap between query and text"""
    if not query or not text:
        return 0.0
    stop_words = {
        "the", "is", "at", "which", "on", "a", "an", "and", "or", "in", "for",
        "to", "of", "with", "what", "how", "can", "i", "my", "me", "tell", "about",
        "are", "do", "does", "did", "be", "been", "being", "have", "has", "had",
        "this", "that", "these", "those", "from", "by", "as", "into"
    }
    q_tokens = [w for w in re.findall(r'[a-zA-Z0-9]+', query.lower()) if w not in stop_words]
    if not q_tokens:
        q_tokens = re.findall(r'[a-zA-Z0-9]+', query.lower())
    if not q_tokens:
        return 0.0
    
    text_lower = text.lower()
    matches = sum(1 for tok in q_tokens if tok in text_lower)
    return matches / len(q_tokens)

class SQLVectorStore:
    @staticmethod
    def search_similar_chunks(
        db: Session,
        query_embedding: List[float],
        top_k: int = 4,
        min_similarity: float = 0.35,
        query_text: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieves top-K most relevant chunks based on vector cosine similarity
        with hybrid keyword scoring fallback for newly ingested documents.
        """
        chunks = db.query(DocumentChunk).all()
        scored_chunks: List[Tuple[float, DocumentChunk]] = []
        has_query_emb = bool(query_embedding and any(query_embedding))
        
        for chunk in chunks:
            vector_score = 0.0
            if has_query_emb and chunk.embedding_vector:
                try:
                    emb = json.loads(chunk.embedding_vector)
                    vector_score = cosine_similarity(query_embedding, emb)
                except Exception:
                    vector_score = 0.0
            
            kw_score = 0.0
            if query_text:
                kw_score = compute_keyword_score(query_text, chunk.content)
            
            if has_query_emb and chunk.embedding_vector:
                # Hybrid score: 80% vector similarity + 20% keyword match
                final_score = (vector_score * 0.8) + (kw_score * 0.2)
            else:
                final_score = kw_score

            # Accept if meets similarity threshold or strong keyword relevance
            if (vector_score >= min_similarity) or (final_score >= 0.30) or (kw_score >= 0.40):
                scored_chunks.append((final_score, chunk))
                
        # Sort descending by similarity score
        scored_chunks.sort(key=lambda x: x[0], reverse=True)
        top_matches = scored_chunks[:top_k]
        
        results: List[Dict[str, Any]] = []
        for score, chunk in top_matches:
            meta = {}
            if chunk.metadata_json:
                try:
                    meta = json.loads(chunk.metadata_json)
                except Exception:
                    pass
            results.append({
                "chunk_id": chunk.id,
                "document_id": chunk.document_id,
                "score": round(score, 4),
                "content": chunk.content,
                "filename": meta.get("filename", "Banking_Policy_Doc"),
                "title": meta.get("title", "Policy Document"),
                "chunk_index": chunk.chunk_index,
                "page_number": meta.get("page_number", chunk.chunk_index + 1)
            })
            
        return results

vector_store = SQLVectorStore()
