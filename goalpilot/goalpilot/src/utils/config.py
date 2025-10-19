"""Configuration management for GoalPilot"""
import os
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # AWS Configuration
    aws_region: str = "us-east-1"
    aws_access_key_id: Optional[str] = None
    aws_secret_access_key: Optional[str] = None
    
    # Bedrock Model
    bedrock_model: str = "anthropic.claude-3-5-sonnet-20240620-v1:0"
    
    # API Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    
    # Application Settings
    environment: str = "local"
    log_level: str = "INFO"
    
    # External APIs
    alpha_vantage_api_key: Optional[str] = None
    
    # Langfuse (Observability)
    langfuse_public_key: Optional[str] = None
    langfuse_secret_key: Optional[str] = None
    langfuse_host: str = "http://localhost:8100"
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"  # ← Ignore extra fields from .env

# Global settings instance
settings = Settings()
