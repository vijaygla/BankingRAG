import hashlib
import json
from datetime import datetime
from typing import Optional, Tuple, List, Dict, Any
from sqlalchemy.orm import Session
from app.models.rag import QueryCache

def normalize_query(query: str) -> str:
    """Normalizes query string for exact hashing"""
    return " ".join(query.lower().strip().split())

def hash_query(normalized_query: str) -> str:
    return hashlib.sha256(normalized_query.encode("utf-8")).hexdigest()

class RAGCacheService:
    @staticmethod
    def get_cached_response(db: Session, query: str) -> Optional[Tuple[str, List[Dict[str, Any]]]]:
        norm = normalize_query(query)
        q_hash = hash_query(norm)
        
        cached_entry = db.query(QueryCache).filter(QueryCache.query_hash == q_hash).first()
        if cached_entry:
            cached_entry.hit_count += 1
            cached_entry.last_hit_at = datetime.utcnow()
            db.commit()
            
            citations = []
            if cached_entry.citations_json:
                try:
                    citations = json.loads(cached_entry.citations_json)
                except Exception:
                    citations = []
            return cached_entry.response_text, citations
            
        return None

    @staticmethod
    def set_cached_response(
        db: Session,
        query: str,
        response_text: str,
        citations: List[Dict[str, Any]]
    ) -> None:
        norm = normalize_query(query)
        q_hash = hash_query(norm)
        
        existing = db.query(QueryCache).filter(QueryCache.query_hash == q_hash).first()
        if not existing:
            new_cache = QueryCache(
                query_hash=q_hash,
                query_text=query[:1000],
                response_text=response_text,
                citations_json=json.dumps(citations),
                hit_count=1,
                last_hit_at=datetime.utcnow()
            )
            db.add(new_cache)
            db.commit()

    @staticmethod
    def clear_all(db: Session) -> int:
        """Clears all cached queries so new document ingestions are immediately reflected."""
        try:
            count = db.query(QueryCache).delete()
            db.commit()
            return count
        except Exception:
            db.rollback()
            return 0

cache_service = RAGCacheService()
