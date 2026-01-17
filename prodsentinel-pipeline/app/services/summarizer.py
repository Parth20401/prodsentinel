from typing import List, Dict, Any
from app.models.raw_signal import RawSignal


def summarize_signals(signals: List[RawSignal]) -> Dict[str, Any]:
    """
    Compress and summarize raw signals to reduce token count.
    
    Strategy:
    1. Filter out DEBUG logs
    2. Extract only essential fields
    3. Truncate stack traces
    4. Group by service and count errors
    """
    if not signals:
        return {"summary": "No signals found", "signals": []}
    
    # Filter and extract essential info
    summarized = []
    error_counts = {}
    
    for signal in signals:
        payload = signal.payload
        
        # Skip DEBUG logs
        if payload.get("level") == "DEBUG":
            continue
        
        # Extract essential fields
        essential = {
            "timestamp": signal.timestamp.isoformat(),
            "service": signal.service_name,
            "type": signal.signal_type.value,
        }
        
        # Add type-specific fields
        if signal.signal_type.value == "log":
            essential["level"] = payload.get("level")
            essential["message"] = payload.get("message")
            
            # Truncate stack traces
            if "stack_trace" in payload:
                lines = payload["stack_trace"].split("\n")
                essential["stack_trace"] = "\n".join(lines[:3]) + "\n..."
            
            # Count errors by service
            if payload.get("level") in ["ERROR", "CRITICAL"]:
                key = f"{signal.service_name}:{payload.get('level')}"
                error_counts[key] = error_counts.get(key, 0) + 1
        
        elif signal.signal_type.value == "trace":
            essential["span_id"] = payload.get("span_id")
            essential["duration_ms"] = payload.get("duration_ms")
            essential["status"] = payload.get("status")
        
        summarized.append(essential)
    
    # Limit to 50 most relevant signals
    if len(summarized) > 50:
        # Prioritize ERROR/CRITICAL logs
        errors = [s for s in summarized if s.get("level") in ["ERROR", "CRITICAL"]]
        others = [s for s in summarized if s.get("level") not in ["ERROR", "CRITICAL"]]
        summarized = errors[:40] + others[:10]
    
    return {
        "total_signals": len(signals),
        "summarized_count": len(summarized),
        "error_counts": error_counts,
        "signals": summarized
    }
