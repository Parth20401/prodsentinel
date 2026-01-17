from pydantic import BaseModel
from typing import List, Optional, Any
from datetime import datetime
from uuid import UUID
from enum import Enum

# Import existing enums to match DB models
# We duplicate them here to avoid circular imports with SQL models if not careful,
# but ideally we'd share them. For now, we define standard str enums for the API.

class IncidentStatus(str, Enum):
    OPEN = "open"
    INVESTIGATING = "investigating"
    RESOLVED = "resolved"
    CLOSED = "closed"

class IncidentSeverity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class IncidentRead(BaseModel):
    id: UUID
    trace_id: str
    status: IncidentStatus
    severity: IncidentSeverity
    detected_at: datetime
    resolved_at: Optional[datetime] = None
    affected_services: List[str]
    error_count: float

    class Config:
        from_attributes = True

class PaginatedIncidentResponse(BaseModel):
    items: List[IncidentRead]
    total: int
    limit: int
    offset: int

class AnalysisResultRead(BaseModel):
    id: UUID
    incident_id: UUID
    root_cause: str
    confidence_score: float
    evidence_signals: List[UUID]
    ai_explanation: Any  # JSON object
    generated_at: datetime

    class Config:
        from_attributes = True
