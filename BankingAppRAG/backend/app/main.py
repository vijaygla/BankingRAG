import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.db.session import engine, SessionLocal, Base
import app.models  # Ensures all SQLAlchemy models are registered
from app.api.api import api_router
from app.services.auth_service import auth_service
from app.services.ingest_service import ingest_service

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("BankingAppRAG")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- STARTUP EVENT ---
    logger.info("Initializing Capgemini BankingAppRAG Backend...")
    
    # 1. Database schema verification & auto-creation
    try:
        logger.info("Verifying MS SQL Server schema tables...")
        Base.metadata.create_all(bind=engine)
        logger.info("MS SQL database tables verified/created successfully.")
    except Exception as e:
        logger.error(f"Error creating database tables: {e}")

    # 2. Super-User Auto-Seeding
    db = SessionLocal()
    try:
        admin_user = auth_service.seed_super_admin(db)
        logger.info(f"Master administrator active: {admin_user.email} (Role: {admin_user.role})")
        
        # 3. Knowledge base auto-seeding for RAG (JSON, TXT, PDF)
        logger.info("Checking baseline banking knowledge base...")
        await ingest_service.seed_sample_knowledge_base(db, admin_user_id=admin_user.id)
    except Exception as e:
        logger.error(f"Startup seeding error: {e}")
    finally:
        db.close()

    yield

    # --- SHUTDOWN EVENT ---
    logger.info("Shutting down BankingAppRAG Backend...")

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Enterprise Banking RAG AI Assistant with MS SQL 2022 and Capgemini Generative Engine",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API V1 router
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/")
def root():
    return {
        "service": settings.PROJECT_NAME,
        "status": "ONLINE",
        "api_v1_docs": "/docs",
        "api_v1_prefix": settings.API_V1_STR
    }
