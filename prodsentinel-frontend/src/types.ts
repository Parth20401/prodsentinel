export type IncidentStatus = "open" | "investigating" | "resolved" | "closed";

export const IncidentStatus = {
    OPEN: "open" as const,
    INVESTIGATING: "investigating" as const,
    RESOLVED: "resolved" as const,
    CLOSED: "closed" as const
};

export type IncidentSeverity = "low" | "medium" | "high" | "critical";

export const IncidentSeverity = {
    LOW: "low" as const,
    MEDIUM: "medium" as const,
    HIGH: "high" as const,
    CRITICAL: "critical" as const
};


export interface Incident {
    id: string; // UUID
    trace_id: string;
    status: IncidentStatus;
    severity: IncidentSeverity;
    detected_at: string; // ISO Date
    resolved_at?: string;
    affected_services: string[];
    error_count: number;
}

export interface AnalysisResult {
    id: string;
    incident_id: string;
    root_cause: string;
    confidence_score: number;
    evidence_signals: string[];
    ai_explanation: any; // JSON
    generated_at: string;
}

export interface PaginatedResponse<T> {
    items: T[];
    total: number;
    limit: number;
    offset: number;
}
