from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from app.models.raw_signal import RawSignal
from app.models.incident import Incident, AnalysisResult

from typing import Optional, List, Any
from datetime import datetime

async def get_signals(
    db: AsyncSession,
    trace_id: Optional[str] = None,
    service_name: Optional[str] = None,
    signal_type: Optional[str] = None,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    limit: int = 100,
    offset: int = 0
):
    """
    Fetch signals with filtering and pagination.
    """
    query = select(RawSignal)
    
    if trace_id:
        query = query.where(RawSignal.trace_id == trace_id)
    if service_name:
        query = query.where(RawSignal.service_name == service_name)
    if signal_type:
        query = query.where(RawSignal.signal_type == signal_type)
    if start_time:
        query = query.where(RawSignal.timestamp >= start_time)
    if end_time:
        query = query.where(RawSignal.timestamp <= end_time)
        
    # Count total for pagination
    count_query = select(func.count()).select_from(query.subquery())
    total = await db.scalar(count_query)
    
    # Apply limit/offset and order
    query = query.order_by(desc(RawSignal.timestamp)).limit(limit).offset(offset)
    
    result = await db.execute(query)
    signals = result.scalars().all()
    
    return signals, total

async def get_trace_signals(db: AsyncSession, trace_id: str):
    """
    Fetch all signals for a specific trace_id, ordered by time.
    """
    query = select(RawSignal).where(RawSignal.trace_id == trace_id).order_by(RawSignal.timestamp)
    result = await db.execute(query)
    return result.scalars().all()


async def get_incidents(
    db: AsyncSession,
    status: Optional[str] = None,
    severity: Optional[str] = None,
    limit: int = 100,
    offset: int = 0
):
    """
    Fetch incidents with optional filtering.
    """
    query = select(Incident)
    
    if status:
        query = query.where(Incident.status == status)
    if severity:
        query = query.where(Incident.severity == severity)
        
    # Count total
    count_query = select(func.count()).select_from(query.subquery())
    total = await db.scalar(count_query) or 0
    
    # Order by most recent detection
    query = query.order_by(desc(Incident.detected_at)).limit(limit).offset(offset)
    
    result = await db.execute(query)
    incidents = result.scalars().all()
    
    return incidents, total


async def get_incident_analysis(db: AsyncSession, incident_id: str):
    """
    Fetch analysis result for a specific incident.
    """
    # Cast str to UUID for safe query
    from uuid import UUID
    try:
        uuid_id = UUID(incident_id)
    except ValueError:
        return None

    query = select(AnalysisResult).where(AnalysisResult.incident_id == uuid_id)
    result = await db.execute(query)
    analysis = result.scalar_one_or_none()
    
    return analysis

