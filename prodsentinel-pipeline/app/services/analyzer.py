import json
from typing import Dict, Any
from autogen import AssistantAgent, UserProxyAgent
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


def generate_trace_report(summarized_data: Dict[str, Any]) -> str:
    """
    Use AutoGen + Gemini to generate root cause analysis.
    
    Args:
        summarized_data: Compressed signal data from summarizer
        
    Returns:
        Markdown-formatted incident report
    """
    logger.info("Initializing AutoGen agents for analysis")
    
    # Configure Gemini model (AutoGen 0.4.x format)
    llm_config = {
        "config_list": [{
            "model": "gemini-2.5-flash",
            "api_key": settings.GOOGLE_API_KEY,
            "api_type": "google"
        }]
    }
    
    # Agent 1: TraceAnalyzer (Assistant)
    analyzer = AssistantAgent(
        name="TraceAnalyzer",
        system_message="""You are an expert SRE analyzing distributed system failures.
        
Your task:
1. Identify the root cause of the incident from the provided signals
2. Determine which service initiated the failure
3. Trace the cascading effects across services
4. Provide a confidence score (0-100)

Be concise and evidence-based. Cite specific log messages or trace spans.""",
        llm_config=llm_config,
    )
    
    # Agent 2: ReportGenerator (UserProxy)
    report_generator = UserProxyAgent(
        name="ReportGenerator",
        human_input_mode="NEVER",
        max_consecutive_auto_reply=0,
        code_execution_config=False,
    )
    
    # Prepare the analysis prompt
    prompt = f"""Analyze this incident:

**Trace ID**: {summarized_data.get('trace_id', 'Unknown')}
**Total Signals**: {summarized_data.get('total_signals', 0)}
**Error Counts**: {json.dumps(summarized_data.get('error_counts', {}), indent=2)}

**Signals**:
```json
{json.dumps(summarized_data.get('signals', []), indent=2)}
```

Provide the report in the following structured format:

1. **Root Cause**: (1-2 sentences summarizing the primary cause).
2. **Affected Services**: (Comma-separated list of service names).
3. **Severity**: (Pick ONE: Critical, High, Medium, Low)
   - *Critical*: Full service outage, data loss, or total payment failure.
   - *High*: Partial outage, degraded core functionality (e.g., slow checkout).
   - *Medium*: Minor impact, non-critical errors (e.g., inventory lookup failures).
   - *Low*: Warnings, retries, or minor performance blips.
4. **Confidence Score**: (Number from 0-100)
5. **Timeline**: (Chronological order of events)
6. **Detailed Conclusion**: (A technical summary of the findings and suggested fixes)

Format as clean Markdown. Use headers for each section. Ensure the fields 'Severity' and 'Confidence Score' are clearly labeled for parsing."""
    
    # Execute analysis
    logger.info("Starting AutoGen conversation")
    report_generator.initiate_chat(analyzer, message=prompt)
    
    # Extract the response
    messages = report_generator.chat_messages[analyzer]
    if messages:
        report = messages[-1]["content"]
        logger.info("Analysis complete")
        return report
    else:
        logger.error("No response from AutoGen agents")
        return "**Error**: Analysis failed - no response from AI agents"
