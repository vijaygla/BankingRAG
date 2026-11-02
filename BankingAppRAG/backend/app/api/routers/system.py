import time
import httpx
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.db.session import get_db
from app.api.deps import get_current_staff, get_current_admin
from app.models.user import User
from app.models.rag import Document, DocumentChunk
from app.schemas.admin import HealthCheckResponse, MetricsTelemetryResponse
from app.services.telemetry_service import telemetry_service
from app.core.config import settings

router = APIRouter(tags=["Infrastructure Health & Telemetry Metrics"])

APP_START_TIME = time.time()

@router.get("/health", response_model=HealthCheckResponse)
async def get_infrastructure_health(
    db: Session = Depends(get_db)
):
    """
    Infrastructure Services Health Monitor (GET /health):
    Core platform running dependencies, connected backends connectivity (MS SQL Server 2022),
    Capgemini Generative Engine API reachability, and vector document chunks count.
    Accessible to STAFF, ADMIN, and platform monitors.
    """
    # 1. Test MS SQL Server
    mssql_ok = False
    try:
        db.execute(text("SELECT 1"))
        mssql_ok = True
    except Exception:
        mssql_ok = False

    # 2. Test Generative Engine connectivity
    ai_ok = False
    try:
        async with httpx.AsyncClient(timeout=4.0) as client:
            res = await client.get(
                f"{settings.CAPGEMINI_AI_ENDPOINT}/models",
                headers={"Authorization": f"Bearer {settings.CAPGEMINI_AI_API_KEY}"}
            )
            ai_ok = (res.status_code == 200)
    except Exception:
        ai_ok = False

    total_docs = db.query(Document).count() if mssql_ok else 0
    total_chunks = db.query(DocumentChunk).count() if mssql_ok else 0
    uptime = round(time.time() - APP_START_TIME, 2)

    overall_status = "HEALTHY" if (mssql_ok and ai_ok) else "DEGRADED"

    return HealthCheckResponse(
        status=overall_status,
        mssql_connected=mssql_ok,
        generative_engine_reachable=ai_ok,
        total_documents=total_docs,
        total_chunks=total_chunks,
        uptime_seconds=uptime
    )

@router.get("/metrics", response_model=MetricsTelemetryResponse)
def get_performance_telemetry_metrics(
    current_user: User = Depends(get_current_staff),
    db: Session = Depends(get_db)
):
    """
    Performance Telemetry Metrics Interface (GET /metrics):
    Model computational latency benchmarks, data consumption token evaluation,
    cache hit ratios, and intent classifier routing profiles.
    """
    return telemetry_service.get_system_metrics(db)
