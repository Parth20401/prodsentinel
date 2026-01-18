"""
Send telemetry to ProdSentinel Ingestion API.
"""
import httpx
import asyncio
from datetime import datetime, timezone
from uuid import uuid4
import os

PRODSENTINEL_URL = os.getenv("PRODSENTINEL_URL", "http://localhost:8000")

async def send_log_to_prodsentinel(
    service_name: str,
    trace_id: str,
    level: str,
    message: str,
    attributes: dict = None
):
    """
    Send a log signal to ProdSentinel backend.
    
    Args:
        service_name: Name of the service emitting the log
        trace_id: Correlation ID
        level: Log level (INFO, ERROR, etc.)
        message: Log message
        attributes: Additional context
    """
    payload = {
        "signal_id": str(uuid4()),
        "trace_id": trace_id,
        "service_name": service_name,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "level": level,
        "message": message,
        "attributes": attributes or {}
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{PRODSENTINEL_URL}/ingest/logs",
                json=payload,
                timeout=10.0  # Increased timeout for cloud backend latency
            )
            response.raise_for_status()
            print(f"[TELEMETRY] Sent log to backend: {service_name} - {message}")
    except Exception as e:
        # Log the error for debugging
        print(f"[TELEMETRY ERROR] Failed to send log: {e}")
        print(f"[TELEMETRY ERROR] URL: {PRODSENTINEL_URL}/ingest/logs")
        print(f"[TELEMETRY ERROR] Payload: {payload}")