"""Configuration management for the form automation agent."""
import os
from typing import Optional
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Azure OpenAI Configuration
    azure_api_key: Optional[str] = None
    azure_endpoint: Optional[str] = None
    azure_deployment_id: str = "gpt-4-turbo"
    # Support multiple environment variable names
    azure_openai_api_key: Optional[str] = None
    azure_openai_key: Optional[str] = None
    azure_openai_endpoint: Optional[str] = None
    azure_model_deployment_name: Optional[str] = None
    azure_openai_model: Optional[str] = None
    
    # Application Settings
    app_name: str = "Safe Form Automation Agent"
    app_version: str = "1.0.0"
    debug: bool = False
    
    # Server Configuration
    host: str = "0.0.0.0"
    port: int = 8000
    # Support PORT from environment
    timeout: int = 30
    
    # Security Settings
    require_approval: bool = True
    max_submissions_per_hour: int = 10
    rate_limit_delay_seconds: int = 6
    max_retry_attempts: int = 3
    
    # Performance Settings
    form_analysis_timeout_sec: int = 30
    submission_timeout_sec: int = 60
    schema_cache_ttl_hours: int = 24
    max_concurrent_submissions: int = 3
    
    # Compliance Settings
    audit_retention_days: int = 90
    encrypt_sensitive_data: bool = True
    
    # Logging
    log_level: str = "INFO"
    log_file: str = "logs/audit.log"
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"  # Ignore extra environment variables not defined in the model


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    settings = Settings()
    
    # Map alternative environment variable names to standard ones
    if not settings.azure_api_key:
        settings.azure_api_key = settings.azure_openai_api_key or settings.azure_openai_key
    
    if not settings.azure_endpoint:
        settings.azure_endpoint = settings.azure_openai_endpoint
    
    if settings.azure_model_deployment_name:
        settings.azure_deployment_id = settings.azure_model_deployment_name
    elif settings.azure_openai_model:
        settings.azure_deployment_id = settings.azure_openai_model
    
    # Support PORT from environment
    if os.getenv("PORT"):
        try:
            settings.port = int(os.getenv("PORT"))
        except ValueError:
            pass
    
    return settings


# Global settings instance
settings = get_settings()
