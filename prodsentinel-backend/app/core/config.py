from pydantic_settings import BaseSettings
from pydantic import field_validator


class Settings(BaseSettings):
    # Application
    APP_NAME: str = "ProdSentinel"
    APP_ENV: str = "local"
    LOG_LEVEL: str = "INFO"
    
    # Database
    DATABASE_URL: str
    
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
    
    # Redis (for Celery task queue)
    REDIS_URL: str = "redis://localhost:6379/0"
    
    @field_validator("REDIS_URL", mode="after")
    @classmethod
    def sanitize_redis_url(cls, v: str) -> str:
        if v and "ssl_cert_reqs=CERT_NONE" in v:
            return v.replace("ssl_cert_reqs=CERT_NONE", "ssl_cert_reqs=none")
        return v
    
    class Config:
        env_file = ".env"

settings = Settings()
