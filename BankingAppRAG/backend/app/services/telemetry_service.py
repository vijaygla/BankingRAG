from typing import Dict
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.rag import ChatHistory, QueryCache
from app.schemas.admin import MetricsTelemetryResponse

class TelemetryService:
    @staticmethod
    def get_system_metrics(db: Session) -> MetricsTelemetryResponse:
        total_queries = db.query(ChatHistory).filter(ChatHistory.role == "user").count()
        
        # Avg Latency & Tokens
        avg_latency = db.query(func.avg(ChatHistory.latency_ms)).filter(ChatHistory.role == "assistant").scalar() or 0.0
        total_tokens = db.query(func.sum(ChatHistory.tokens_used)).filter(ChatHistory.role == "assistant").scalar() or 0
        
        # Cache hits
        cache_hits = db.query(func.sum(QueryCache.hit_count)).scalar() or 0
        total_policy_queries = db.query(ChatHistory).filter(ChatHistory.intent == "POLICY_DOC", ChatHistory.role == "user").count()
        cache_hit_rate = round((cache_hits / total_policy_queries * 100), 2) if total_policy_queries > 0 else 0.0

        # Intent distribution
        intent_records = db.query(ChatHistory.intent, func.count(ChatHistory.id)).filter(ChatHistory.role == "user").group_by(ChatHistory.intent).all()
        intent_dist: Dict[str, int] = {rec[0] or "UNKNOWN": rec[1] for rec in intent_records}

        # Model distribution
        model_records = db.query(ChatHistory.model_used, func.count(ChatHistory.id)).filter(ChatHistory.role == "assistant").group_by(ChatHistory.model_used).all()
        model_dist: Dict[str, int] = {rec[0] or "Default": rec[1] for rec in model_records}

        return MetricsTelemetryResponse(
            total_queries=total_queries,
            avg_latency_ms=round(float(avg_latency), 2),
            total_tokens_used=int(total_tokens),
            cache_hit_count=int(cache_hits),
            cache_hit_rate_pct=cache_hit_rate,
            intent_distribution=intent_dist,
            model_distribution=model_dist
        )

telemetry_service = TelemetryService()
