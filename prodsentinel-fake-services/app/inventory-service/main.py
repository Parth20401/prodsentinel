from fastapi import FastAPI, Request, HTTPException
import asyncio
from common.logging import setup_logging
from common.tracing import setup_tracing
from common.middleware import request_context_middleware
from common.telemetry_sender import send_log_to_prodsentinel
from service import check_inventory

app = FastAPI()
app.middleware("http")(request_context_middleware)

SERVICE_NAME = "inventory-service"
logger = setup_logging(SERVICE_NAME)
tracer = setup_tracing(SERVICE_NAME)

@app.get("/inventory/{item_id}")
async def inventory(item_id: str, request: Request):
    trace_id = request.state.request_id
    
    with tracer.start_as_current_span("check_inventory") as span:
        span.set_attribute("item.id", item_id)

        try:
            result = check_inventory(item_id)

            logger.info(
                "Inventory check completed",
                request_id=trace_id,
                item_id=item_id,
                available=result["available"],
                latency_ms=result["latency_ms"]
            )
            
            asyncio.create_task(send_log_to_prodsentinel(
                service_name=SERVICE_NAME,
                trace_id=trace_id,
                level="INFO",
                message="Inventory check completed",
                attributes={
                    "item_id": item_id, 
                    "available": result["available"],
                    "latency_ms": result["latency_ms"]
                }
            ))
            
            return result

        except Exception as e:
            logger.error(
                "Inventory check failed",
                request_id=trace_id,
                item_id=item_id,
                error=str(e),
                error_type=type(e).__name__
            )
            
            asyncio.create_task(send_log_to_prodsentinel(
                service_name=SERVICE_NAME,
                trace_id=trace_id,
                level="ERROR",
                message="Inventory check failed",
                attributes={
                    "item_id": item_id, 
                    "error": str(e),
                    "error_type": type(e).__name__
                }
            ))
            
            raise HTTPException(status_code=500, detail="Inventory failure")
