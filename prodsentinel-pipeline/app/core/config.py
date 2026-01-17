from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "ProdSentinel Pipeline"
    APP_ENV: str = "development"
    LOG_LEVEL: str = "INFO"
    
    # Redis (Broker)
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Postgres (Backend for Results)
    DATABASE_URL: str = "postgresql+asyncpg://prodsentinel:prodsentinel@localhost:5432/prodsentinel"
    
    # AI Config
    GOOGLE_API_KEY: str

    class Config:
        env_file = ".env"

settings = Settings()
