from fastapi import FastAPI, status
from fastapi.responses import JSONResponse
from app.core.logging import setup_logging, get_logger
from app.core.config import settings
from app.tasks.analysis import analyze_trace

# Initialize logging
setup_logging(log_level=settings.LOG_LEVEL)
logger = get_logger(__name__)

app = FastAPI(title="ProdSentinel Pipeline - Management API")


@app.on_event("startup")
async def startup_event():
    """Log application startup."""
    logger.info(
        f"Starting {settings.APP_NAME} in {settings.APP_ENV} environment"
    )


@app.on_event("shutdown")
async def shutdown_event():
    """Log application shutdown."""
    logger.info(f"Shutting down {settings.APP_NAME}")


@app.get("/health")
async def health_check():
    """
    Health check endpoint for Kubernetes/Docker probes.
    """
    return {
        "status": "healthy",
        "service": "prodsentinel-pipeline",
        "environment": settings.APP_ENV
    }


@app.post("/debug/analyze/{trace_id}", status_code=status.HTTP_202_ACCEPTED)
async def debug_analyze(trace_id: str):
    """
    Manually trigger analysis for a trace (bypasses Redis queue).
    Useful for development and debugging.
    
    Args:
        trace_id: The trace ID to analyze
    """
    logger.info(f"Manual analysis triggered for trace_id: {trace_id}")
    
    try:
        # Trigger Celery task
        task = analyze_trace.delay(trace_id)
        
        return {
            "status": "accepted",
            "trace_id": trace_id,
            "task_id": task.id,
            "message": "Analysis task queued"
        }
    except Exception as exc:
        logger.error(f"Failed to queue analysis task: {exc}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"error": str(exc)}
        )


@app.get("/")
async def root():
    """Root endpoint with service info."""
    return {
        "service": "ProdSentinel Pipeline",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "debug_analyze": "/debug/analyze/{trace_id}"
        }
    }
