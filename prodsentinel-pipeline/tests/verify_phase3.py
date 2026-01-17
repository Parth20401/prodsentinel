import asyncio
import uuid
import json
from unittest.mock import MagicMock, patch, AsyncMock
from datetime import datetime

# Mock the settings first
with patch("app.core.config.settings") as mock_settings:
    mock_settings.GOOGLE_API_KEY = "fake_key"
    mock_settings.REDIS_URL = "redis://localhost:6379/0"
    mock_settings.DATABASE_URL = "postgresql+asyncpg://user:pass@localhost:5432/db"

    from app.services.summarizer import summarize_signals
    from app.services.analyzer import generate_trace_report
    from app.tasks.analysis import analyze_trace, _analyze_trace_async
    from app.models.raw_signal import RawSignal, SignalTypeEnum

def test_summarizer_logic():
    """Test that logs are correctly compressed."""
    print("Testing Summarizer Logic...")
    
    signals = []
    trace_id = "test-trace-123"
    
    # Create 100 DEBUG logs (should be ignored)
    for i in range(100):
        signals.append(RawSignal(
            id=uuid.uuid4(),
            signal_type=SignalTypeEnum.log,
            trace_id=trace_id,
            service_name="service-a",
            timestamp=datetime.now(),
            payload={"level": "DEBUG", "message": f"debug msg {i}"}
        ))
        
    # Create 5 ERROR logs (should be kept)
    for i in range(5):
        signals.append(RawSignal(
            id=uuid.uuid4(),
            signal_type=SignalTypeEnum.log,
            trace_id=trace_id,
            service_name="service-b",
            timestamp=datetime.now(),
            payload={
                "level": "ERROR", 
                "message": "Critical failure", 
                "stack_trace": "Frame 1\nFrame 2\nFrame 3\nFrame 4\nFrame 5"
            }
        ))

    summary = summarize_signals(signals)
    
    # Assertions
    assert summary["total_signals"] == 105
    assert summary["summarized_count"] == 5
    assert len(summary["signals"]) == 5
    assert summary["error_counts"] == {"service-b:ERROR": 5}
    assert "Frame 5" not in summary["signals"][0]["stack_trace"] # Should be truncated
    
    print("✅ Summarizer Logic Passed")


@patch("app.tasks.analysis.AsyncSessionLocal")
@patch("app.tasks.analysis.generate_trace_report")
async def test_async_analysis_flow(mock_report, mock_db_cls):
    """Test the full analysis orchestration (mocked DB)."""
    print("\nTesting Analysis Flow...")
    
    # Mock DB Session
    mock_session = AsyncMock() # Use AsyncMock for async context manager
    mock_db_cls.return_value.__aenter__.return_value = mock_session
    
    # Mock DB Query Result
    mock_result = MagicMock()
    # scalars().all() pattern
    mock_result.scalars.return_value.all.return_value = [
        RawSignal(
            id=uuid.uuid4(),
            signal_type=SignalTypeEnum.log,
            trace_id="trace-abc",
            service_name="payment",
            timestamp=datetime.now(),
            payload={"level": "ERROR", "message": "Payment failed"}
        )
    ]
    mock_session.execute.return_value = mock_result
    
    # Mock AI Report
    mock_report.return_value = "**Root Cause**: Payment gateway timeout"
    
    # Run Function
    result = await _analyze_trace_async("trace-abc")
    
    # Assertions
    assert result["status"] == "success"
    assert result["trace_id"] == "trace-abc"
    assert "Payment gateway timeout" in result["report"]
    mock_report.assert_called_once()
    
    print("✅ Analysis Flow Passed")

if __name__ == "__main__":
    try:
        test_summarizer_logic()
        asyncio.run(test_async_analysis_flow())
        print("\n🎉 ALL TESTS PASSED")
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR: {e}")
