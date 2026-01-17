from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from app.models.raw_signal import RawSignal
from app.core.logging import get_logger
from uuid import UUID

logger = get_logger(__name__)


async def ingest_signal(
    db: AsyncSession,
    signal_id: UUID,
    signal_type: str,
    trace_id: str,
    service_name: str,
    timestamp,
    payload: dict,
):
    """
    Core ingestion logic.
    Stateless, idempotent, safe to retry.
    
    Args:
        db: Database session
        signal_id: Unique signal identifier
        signal_type: Type of signal (log, trace, metric)
        trace_id: Correlation ID for distributed tracing
        service_name: Name of the service emitting the signal
        timestamp: Signal timestamp
        payload: Full signal payload as dict
    """
    logger.debug(f"Processing {signal_type} signal: {signal_id}")
    
    try:
        raw = RawSignal(
            id=signal_id,
            signal_type=signal_type,
            trace_id=trace_id,
            service_name=service_name,
            timestamp=timestamp,
            payload=payload,
        )

        db.add(raw)
        
        # 4. Handle Incident Tracking (Unified for all signals)
        from app.models.incident import Incident, IncidentStatus, IncidentSeverity
        from sqlalchemy import select
        
        # Check for existing incident
        stmt = select(Incident).where(Incident.trace_id == trace_id)
        result = await db.execute(stmt)
        existing_incident = result.scalar_one_or_none()
        
        current_severity = IncidentSeverity.LOW
        if signal_type == "log" and payload.get("level") in ["ERROR", "CRITICAL"]:
            current_severity = IncidentSeverity.HIGH
        elif signal_type == "metric" and "latency" in payload.get("metric_name", "").lower():
            if payload.get("value", 0) >= 2000:
                current_severity = IncidentSeverity.HIGH

        if existing_incident:
            # Update existing
            if service_name not in existing_incident.affected_services:
                existing_incident.affected_services = list(set(existing_incident.affected_services + [service_name]))
            
            existing_incident.error_count += 1
            
            # Upgrade severity if current signal is more severe
            severity_order = {IncidentSeverity.LOW: 0, IncidentSeverity.MEDIUM: 1, IncidentSeverity.HIGH: 2, IncidentSeverity.CRITICAL: 3}
            if severity_order.get(current_severity, 0) > severity_order.get(existing_incident.severity, 0):
                existing_incident.severity = current_severity
        else:
            # Create new incident entry so it shows in charts immediately
            new_incident = Incident(
                trace_id=trace_id,
                status=IncidentStatus.OPEN,
                severity=current_severity,
                affected_services=[service_name],
                error_count=1
            )
            db.add(new_incident)

        await db.commit()
        logger.info(f"Signal stored and incident tracked: {signal_type} from {service_name}")
        
        # 5. Triage Layer: Trigger expensive AI analysis only for "Important" signals
        should_trigger = False
        
        if current_severity == IncidentSeverity.HIGH:
            should_trigger = True
        elif "fail" in str(payload).lower() or "critical" in str(payload).lower():
            should_trigger = True

        if should_trigger:
            try:
                _trigger_analysis(trace_id)
            except Exception as exc:
                # Don't fail ingestion if analysis trigger fails
                logger.error(f"Failed to trigger analysis for {trace_id}: {exc}")
        
    except SQLAlchemyError as exc:
        await db.rollback()
        logger.error(f"Database error during ingestion: {exc}", exc_info=True)
        raise
        
    except Exception as exc:
        await db.rollback()
        logger.error(f"Unexpected error during ingestion: {exc}", exc_info=True)
        raise




def _trigger_analysis(trace_id: str):
    """
    Trigger async analysis via Celery (Fire and Forget).
    
    This is called synchronously but queues the task asynchronously.
    Uses a countdown to debounce multiple errors from the same trace.
    Deduplicates using Redis to ensure only one analysis task per trace_id.
    """
    try:
        import redis
        from celery import Celery
        from app.core.config import settings
        
        # Redis-based deduplication
        # Use a new connection for safety (or could use a connection pool)
        r = redis.from_url(settings.REDIS_URL, decode_responses=True)
        key = f"analysis:triggered:{trace_id}"
        
        # Check if already triggered (set if Not Exists)
        # Expires in 300s (5 mins) to allow re-analysis later if needed
        if not r.set(key, "1", ex=300, nx=True):
            logger.debug(f"Analysis already queued for trace_id: {trace_id}, skipping duplicate trigger")
            return
        
        # Create minimal Celery client (just for sending tasks)
        celery_client = Celery(broker=settings.REDIS_URL)
        
        # Queue analysis with 60s delay (debounce window)
        celery_client.send_task(
            "analyze_trace",
            args=[trace_id],
            countdown=60
        )
        
        logger.info(f"Analysis queued for trace_id: {trace_id} (60s delay)")
        
    except Exception as exc:
        # If queuing fails, delete key so it can be retried
        try:
            r = redis.from_url(settings.REDIS_URL, decode_responses=True)
            r.delete(f"analysis:triggered:{trace_id}")
        except:
            pass
            
        logger.error(f"Failed to queue Celery task: {exc}", exc_info=True)
        raise

