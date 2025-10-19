"""
Configuration settings loaded from environment variables
"""
import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()

class Settings:
    """Application settings"""
    
    # AWS Bedrock
    aws_region: str = os.getenv("AWS_REGION", "us-east-1")
    bedrock_model: str = os.getenv("BEDROCK_MODEL", "anthropic.claude-3-5-sonnet-20240620-v1:0")
    
    # API Settings
    api_port: int = int(os.getenv("API_PORT", "8000"))
    
    # Alpha Vantage (optional)
    alpha_vantage_api_key: str = os.getenv("ALPHA_VANTAGE_API_KEY", "demo")
    
    # Logging
    log_level: str = os.getenv("LOG_LEVEL", "INFO")

# Global instance
settings = Settings()

__all__ = ["settings"]
