"""
Centralized structured logging configuration.
All services import from here to ensure consistent log format.
"""

import logging
import structlog

def setup_logging(service_name: str):
    """
    Configures JSON structured logging with service metadata.
    """

    logging.basicConfig(level=logging.INFO)

    structlog.configure(
        processors=[
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.add_log_level,
            structlog.processors.JSONRenderer()
        ]
    )

    return structlog.get_logger(service=service_name)
