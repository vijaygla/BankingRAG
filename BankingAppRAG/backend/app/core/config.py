import os
from typing import List
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Capgemini BankingAppRAG"
    API_V1_STR: str = "/api/v1"
    
    # Database
    DATABASE_URL: str = "mssql+pyodbc://sa:Capgemini%4012345@LIN-5CD6268KRS/BankingAppRAG?driver=ODBC+Driver+18+for+SQL+Server&TrustServerCertificate=yes&Encrypt=yes"
    
    # Security / JWT
    JWT_SECRET: str = "c6b547285627f12e8b2b6c164a6d36e890c0a34b21e8b4e78a2e1d7f6c5b4a39"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 Hours
    
    # AI Engine
    CAPGEMINI_AI_API_KEY: str = "sk-x3FOSdELzRNhQ1fpzloftA"
    CAPGEMINI_AI_ENDPOINT: str = "https://openai.generative.engine.capgemini.com/v1"
    DEFAULT_AI_MODEL: str = "openai.gpt-5"
    EMBEDDING_MODEL: str = "text-embedding-3-small"
    ALLOWED_AI_MODELS: List[str] = [
        "openai.gpt-5",
        "openai.gpt-4o",
        "anthropic.claude-opus-4-6-v1",
        "grok-4"
    ]
    
    # Super-User Admin Default Seed
    ADMIN_EMAIL: str = "admin@capgemini-bank.com"
    ADMIN_PASSWORD: str = "Admin@Capgemini123"
    ADMIN_NAME: str = "System Super Admin"
    
    # RAG Chunking Parameters
    CHUNK_SIZE_TOKENS: int = 800
    CHUNK_OVERLAP_TOKENS: int = 120

    class Config:
        env_file = ".env"
        extra = "allow"

settings = Settings()
