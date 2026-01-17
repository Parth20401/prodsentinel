import logging
import sys
from app.core.config import settings

def setup_logging(log_level: str = None):
    """Configure structured logging for the pipeline service."""
    level = log_level or settings.LOG_LEVEL
    
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[logging.StreamHandler(sys.stdout)]
    )

def get_logger(name: str) -> logging.Logger:
    """Get a logger instance."""
    return logging.getLogger(name)
