from typing import Dict, Any, List, Optional
from pydantic import BaseModel

class IngestResponse(BaseModel):
    message: str
    filename: str
    file_type: str
    total_chunks: int
    document_id: int

class HealthCheckResponse(BaseModel):
    status: str
    mssql_connected: bool
    generative_engine_reachable: bool
    total_documents: int
    total_chunks: int
    uptime_seconds: float

class MetricsTelemetryResponse(BaseModel):
    model_config = {"protected_namespaces": ()}
    total_queries: int
    avg_latency_ms: float
    total_tokens_used: int
    cache_hit_count: int
    cache_hit_rate_pct: float
    intent_distribution: Dict[str, int]
    model_distribution: Dict[str, int]
