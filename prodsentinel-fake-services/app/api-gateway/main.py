from fastapi import FastAPI, Request, HTTPException
import httpx
import asyncio
from app.common.logging import setup_logging
from app.common.tracing import setup_tracing
from app.common.middleware import request_context_middleware
from app.common.telemetry_sender import send_log_to_prodsentinel

PAYMENT_URL = "http://localhost:8004"
SERVICE_NAME = "api-gateway"

app = FastAPI()
app.middleware("http")(request_context_middleware)

logger = setup_logging(SERVICE_NAME)
tracer = setup_tracing(SERVICE_NAME)

@app.post("/checkout/{order_id}")
async def checkout(order_id: str, request: Request):
    trace_id = request.state.request_id
    
    with tracer.start_as_current_span("checkout") as span:
        span.set_attribute("order.id", order_id)

        # Local logging
        logger.info(
            "Checkout initiated",
            request_id=trace_id,
            order_id=order_id
        )
        
        # Send telemetry to ProdSentinel (fire and forget)
        asyncio.create_task(send_log_to_prodsentinel(
            service_name=SERVICE_NAME,
            trace_id=trace_id,
            level="INFO",
            message="Checkout initiated",
            attributes={"order_id": order_id}
        ))

        try:
            async with httpx.AsyncClient() as client:
                resp = await client.post(f"{PAYMENT_URL}/pay/{order_id}", headers={"x-request-id": trace_id})
                resp.raise_for_status()

            logger.info(
                "Checkout completed",
                request_id=trace_id,
                order_id=order_id
            )
            
            asyncio.create_task(send_log_to_prodsentinel(
                service_name=SERVICE_NAME,
                trace_id=trace_id,
                level="INFO",
                message="Checkout completed",
                attributes={"order_id": order_id}
            ))
            
            return {"status": "SUCCESS"}

        except Exception as e:
            logger.error(
                "Checkout failed",
                request_id=trace_id,
                order_id=order_id,
                error=str(e)
             )
            
            asyncio.create_task(send_log_to_prodsentinel(
                service_name=SERVICE_NAME,
                trace_id=trace_id,
                level="ERROR",
                message="Checkout failed",
                attributes={"order_id": order_id, "error": str(e)}
            ))
            
            raise HTTPException(status_code=500, detail="Checkout failure")
