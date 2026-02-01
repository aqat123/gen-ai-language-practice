from pydantic_settings import BaseSettings
from typing import Optional, Union
from pydantic import field_validator
import json


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Database
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/language_app"

    # LLM API Configuration
    LLM_API_KEY: str
    LLM_API_BASE_URL: str = "https://generativelanguage.googleapis.com/v1beta"
    LLM_MODEL: str = "gemini-2.5-flash"

    # Image Generation API Configuration (Legacy - not used with Vertex AI)
    LLM_IMAGE_API_KEY: str = ""
    LLM_IMAGE_API_BASE_URL: str = "https://generativelanguage.googleapis.com/v1beta"
    LLM_IMAGE_MODEL: str = "imagen-4.0-generate-001"

    # Vertex AI Configuration for Imagen
    VERTEX_AI_PROJECT_ID: Optional[str] = None
    VERTEX_AI_LOCATION: str = "us-central1"
    VERTEX_AI_CREDENTIALS_PATH: str = "credentials/service-account-key.json"
    USE_VERTEX_AI: bool = False  # Set to True to enable Vertex AI images

    # Speech-to-Text API Configuration
    STT_API_KEY: str
    STT_API_BASE_URL: str = "https://generativelanguage.googleapis.com/v1beta"
    STT_MODEL: str = "gemini-2.5-flash"

    # Application Configuration
    ENV: str = "dev"
    DEBUG: bool = True
    API_V1_PREFIX: str = "/api/v1"
    PROJECT_NAME: str = "Language Learning Backend"

    # JWT Authentication
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # CEFR Levels
    CEFR_LEVELS: list = ["A1", "A2", "B1", "B2", "C1", "C2"]

    # Redis Cache Configuration
    REDIS_URL: str = "redis://localhost:6379/0"
    CACHE_ENABLED: bool = True
    CACHE_TTL_HOURS: int = 24
    VALIDATION_CACHE_TTL_MINUTES: int = 60
    RECENT_WORDS_CACHE_TTL_MINUTES: int = 5

    # CORS
    BACKEND_CORS_ORIGINS: Union[list, str] = ["*"]

    @field_validator('BACKEND_CORS_ORIGINS', mode='before')
    @classmethod
    def parse_cors_origins(cls, v):
        """Parse CORS origins from environment variable."""
        if isinstance(v, str):
            # Handle JSON string format like '["*"]' or '["http://localhost:3000"]'
            try:
                return json.loads(v)
            except json.JSONDecodeError:
                # Handle comma-separated format like "*" or "http://localhost:3000,http://localhost:8080"
                return [origin.strip() for origin in v.split(',')]
        return v

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
