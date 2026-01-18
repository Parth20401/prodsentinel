from pydantic_settings import BaseSettings
from pydantic import field_validator

class Settings(BaseSettings):
    APP_NAME: str = "ProdSentinel Pipeline"
    APP_ENV: str = "development"
    LOG_LEVEL: str = "INFO"
    
    # Redis (Broker)
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Postgres (Backend for Results)
    DATABASE_URL: str = "postgresql+asyncpg://prodsentinel:prodsentinel@localhost:5432/prodsentinel"
    
    @field_validator("DATABASE_URL", mode="after")
    @classmethod
    def sanitize_db_url(cls, v: str) -> str:
        if v and ("sslmode=" in v or "channel_binding=" in v):
            from urllib.parse import urlparse, urlunparse, parse_qs, urlencode
            u = urlparse(v)
            query = parse_qs(u.query)
            query.pop("sslmode", None)
            query.pop("channel_binding", None)
            return urlunparse(u._replace(query=urlencode(query, doseq=True)))
        return v
    
    # AI Config
    GOOGLE_API_KEY: str

    class Config:
        env_file = ".env"

settings = Settings()
