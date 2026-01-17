from sqlalchemy import select
from app.celery_app import celery_app
from app.core.database import get_engine, get_session_factory
from app.core.logging import get_logger
from app.models.raw_signal import RawSignal
from app.services.summarizer import summarize_signals
from app.services.analyzer import generate_trace_report

logger = get_logger(__name__)


@celery_app.task(name="analyze_trace", bind=True, max_retries=3)
def analyze_trace(self, trace_id: str):
    # ... (unchanged task wrapper) ...
    import asyncio
    
    logger.info(f"Starting analysis for trace_id: {trace_id}")
    
    try:
        # Run async logic in sync Celery task
        result = asyncio.run(_analyze_trace_async(trace_id))
        logger.info(f"Analysis complete for trace_id: {trace_id}")
        return result
        
    except Exception as exc:
        logger.error(f"Analysis failed for trace_id {trace_id}: {exc}", exc_info=True)
        # Don't retry - let it fail permanently to avoid duplicate analysis
        raise


async def _analyze_trace_async(trace_id: str) -> dict:
    """Async implementation of trace analysis."""
    
    # Create engine/session specific to this loop (safe for asyncio.run)
    engine = get_engine()
    AsyncSessionLocal = get_session_factory(engine)
    
    try:
        # 1. Fetch signals from DB
        # 1. Fetch signals from DB
        async with AsyncSessionLocal() as db:
            query = select(RawSignal).where(RawSignal.trace_id == trace_id).order_by(RawSignal.timestamp)
            result = await db.execute(query)
            signals = result.scalars().all()
        
            if not signals:
                logger.warning(f"No signals found for trace_id: {trace_id}")
                await engine.dispose()
                return {"status": "no_signals", "trace_id": trace_id}
            
            logger.info(f"Found {len(signals)} signals for trace_id: {trace_id}")
            
            # 2. Summarize signals
            summarized = summarize_signals(signals)
            summarized["trace_id"] = trace_id
            
            logger.info(f"Summarized to {summarized['summarized_count']} signals")
            
            # 3. Run AI analysis
            report = generate_trace_report(summarized)
            
            # 4. Save to DB
            import re
            from app.models.incident import Incident, AnalysisResult, IncidentStatus, IncidentSeverity
            
            # Simple parsing logic for Confidence and Severity
            confidence_match = re.search(r"Confidence Score\D*(\d+)", report)
            confidence = float(confidence_match.group(1)) if confidence_match else 50.0

            severity = IncidentSeverity.HIGH
            severity_match = re.search(r"Severity\D*(Critical|High|Medium|Low)", report, re.IGNORECASE)
            if severity_match:
                found_severity = severity_match.group(1).lower()
                if found_severity == "critical": severity = IncidentSeverity.CRITICAL
                elif found_severity == "medium": severity = IncidentSeverity.MEDIUM
                elif found_severity == "low": severity = IncidentSeverity.LOW

            # Determine affected services from signals
            affected_services_list = list(set(s.service_name for s in signals if s.service_name))
            
            # Check for existing incident
            stmt = select(Incident).where(Incident.trace_id == trace_id)
            existing_incident = (await db.execute(stmt)).scalar_one_or_none()
            
            incident_id = None
            if existing_incident:
                logger.info(f"Updating existing incident for trace_id: {trace_id}")
                existing_incident.error_count = len(signals)
                # Update services if new ones appeared
                existing_incident.affected_services = list(set(existing_incident.affected_services + affected_services_list))
                # Update severity to AI-determined value
                existing_incident.severity = severity
                incident_id = existing_incident.id
            else:
                logger.info(f"Creating new incident for trace_id: {trace_id}")
                new_incident = Incident(
                    trace_id=trace_id,
                    status=IncidentStatus.OPEN,
                    severity=severity,
                    affected_services=affected_services_list,
                    error_count=len(signals)
                )
                db.add(new_incident)
                await db.flush()
                incident_id = new_incident.id
                
            # Create Analysis Result
            analysis_entry = AnalysisResult(
                incident_id=incident_id,
                root_cause=report, # Storing full report text as root cause for visibility
                confidence_score=confidence,
                evidence_signals=[s.id for s in signals],
                ai_explanation={"full_report": report}
            )
            db.add(analysis_entry)
            await db.commit()
            
            logger.info(f"Saved analysis result for incident_id: {incident_id}")
            
            return {
                "status": "success",
                "trace_id": trace_id,
                "report": report,
                "signal_count": len(signals),
                "error_counts": summarized.get("error_counts", {})
            }


    finally:
        # Always clean up the engine
        await engine.dispose()
    

