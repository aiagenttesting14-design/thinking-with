from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # API Settings
    app_name: str = "Research Synthesis API"
    debug: bool = False
    cors_origins: list = ["http://localhost:3000", "http://localhost:8000"]
    
    # Database
    database_url: str = "sqlite:///./research.db"
    
    # Redis
    redis_url: str = "redis://localhost:6379"
    
    # AI Services
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    pinecone_api_key: Optional[str] = None
    pinecone_environment: str = "us-east1-gcp"
    
    # Model Configuration
    default_llm_model: str = "gpt-3.5-turbo"
    embedding_model: str = "text-embedding-3-small"
    summarization_model: str = "gpt-3.5-turbo"
    synthesis_model: str = "gpt-4"
    
    # Processing Settings
    max_file_size_mb: int = 50
    chunk_size_tokens: int = 1000
    chunk_overlap_tokens: int = 100
    max_documents_per_user: int = 1000
    
    # Rate Limiting
    requests_per_minute: int = 60
    documents_per_day: int = 100
    
    # Storage
    upload_dir: str = "./uploads"
    max_retention_days: int = 30
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
