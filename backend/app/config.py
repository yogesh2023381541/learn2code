import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    database_url: str = os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg://learn2code:learn2code@localhost:5432/learn2code",
    )
    jwt_secret: str = os.getenv("JWT_SECRET", "change-me-before-deploying")
    access_token_minutes: int = int(os.getenv("ACCESS_TOKEN_MINUTES", "30"))
    refresh_token_days: int = int(os.getenv("REFRESH_TOKEN_DAYS", "30"))
    frontend_origin: str = os.getenv("FRONTEND_ORIGIN", "http://localhost:5173")
    ai_provider_url: str = os.getenv("AI_PROVIDER_URL", "")
    ai_provider_api_key: str = os.getenv("AI_PROVIDER_API_KEY", "")
    ai_provider_model: str = os.getenv("AI_PROVIDER_MODEL", "gpt-4o-mini")
    ai_max_tokens: int = int(os.getenv("AI_MAX_TOKENS", "1200"))
    ai_requests_per_minute: int = int(os.getenv("AI_REQUESTS_PER_MINUTE", "20"))


settings = Settings()
