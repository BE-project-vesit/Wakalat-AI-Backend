"""
Configuration management for Wakalat-AI MCP Server
"""
import os
from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Server Configuration
    mcp_server_name: str = "wakalat-ai-legal-assistant"
    mcp_server_version: str = "1.0.0"
    mcp_server_port: int = 8000
    
    # AI Model Configuration
    openai_api_key: Optional[str] = None
    openai_model: str = "gpt-4-turbo-preview"
    openai_embedding_model: str = "text-embedding-3-small"
    
    anthropic_api_key: Optional[str] = None
    anthropic_model: str = "claude-3-opus-20240229"
    
    # Vector Database
    chroma_persist_directory: Path = Path("./data/chroma")
    chroma_collection_name: str = "legal_cases"
    
    # Supabase Configuration
    supabase_url: Optional[str] = None
    supabase_key: Optional[str] = None
    
    # Database
    database_url: str = "sqlite:///./data/wakalat.db"
    
    # Indian Legal Resources
    indiankanoon_base_url: str = "https://indiankanoon.org"
    supreme_court_api_url: str = "https://api.sci.gov.in"
    high_court_api_url: str = "https://example-highcourt-api.gov.in"
    
    # Document Storage
    document_storage_path: Path = Path("./data/documents")
    max_document_size_mb: int = 50
    
    # Logging
    log_level: str = "INFO"
    log_file: Path = Path("./logs/wakalat-ai.log")
    
    # Rate Limiting
    rate_limit_per_minute: int = 60
    max_concurrent_requests: int = 10
    
    # Cache
    cache_ttl_seconds: int = 3600
    enable_cache: bool = True
    
    # Security
    secret_key: str = "change-this-secret-key-in-production"
    allowed_origins: str = "http://localhost:3000,http://localhost:5173"
    
    # Feature Flags
    enable_precedent_search: bool = True
    enable_case_law_search: bool = True
    enable_document_generation: bool = True
    enable_legal_research: bool = True
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Create necessary directories
        self.chroma_persist_directory.mkdir(parents=True, exist_ok=True)
        self.document_storage_path.mkdir(parents=True, exist_ok=True)
        self.log_file.parent.mkdir(parents=True, exist_ok=True)


# Global settings instance
settings = Settings()
