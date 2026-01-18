from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# Create async engine
# Note: For Celery tasks using asyncio.run(), we need to create the engine
# inside the loop to avoid "future attached to a different loop" errors.

from sqlalchemy.pool import NullPool

def get_engine():
    """Create a new async engine instance."""
    # Use NullPool for Celery workers to prevent connection holding across loops
    return create_async_engine(
        settings.DATABASE_URL, 
        echo=False, 
        poolclass=NullPool,
        connect_args={
            "timeout": 60, 
            "command_timeout": 60,
            "server_settings": {
                "application_name": "prodsentinel-pipeline"
            }
        }
    )

def get_session_factory(engine):
    """Create a session factory for the given engine."""
    return sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

# Keep global for FastAPI (which shares a persistent loop)
engine = get_engine()
AsyncSessionLocal = get_session_factory(engine)

async def get_db():
    """Database session dependency for FastAPI."""
    async with AsyncSessionLocal() as session:
        yield session
