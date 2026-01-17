from fastapi import FastAPI, Request, HTTPException
import asyncio
from common.logging import setup_logging
from common.tracing import setup_tracing
from common.middleware import request_context_middleware
from common.telemetry_sender import send_log_to_prodsentinel
from service import authorize_payment

app = FastAPI()
app.middleware("http")(request_context_middleware)

SERVICE_NAME = "payment-service"
logger = setup_logging(SERVICE_NAME)
tracer = setup_tracing(SERVICE_NAME)

@app.post("/pay/{order_id}")
async def pay(order_id: str, request: Request):
    trace_id = request.state.request_id
    
    with tracer.start_as_current_span("authorize_payment") as span:
        span.set_attribute("order.id", order_id)

        try:
            result = await authorize_payment(order_id, "item-123", trace_id)

            logger.info(
                "Payment authorized",
                request_id=trace_id,
                order_id=order_id,
                latency_ms=result["latency_ms"]
            )
            
            asyncio.create_task(send_log_to_prodsentinel(
                service_name=SERVICE_NAME,
                trace_id=trace_id,
                level="INFO",
                message="Payment authorized",
                attributes={
                    "order_id": order_id, 
                    "latency_ms": result["latency_ms"]
                }
            ))
            
            return result

        except TimeoutError:
            logger.error(
                "Payment timeout",
                request_id=trace_id,
                order_id=order_id,
                error_code="PAYMENT_TIMEOUT",
                retryable=True
            )
            
            asyncio.create_task(send_log_to_prodsentinel(
                service_name=SERVICE_NAME,
                trace_id=trace_id,
                level="ERROR",
                message="Payment timeout",
                attributes={
                    "order_id": order_id, 
                    "error_code": "PAYMENT_TIMEOUT",
                    "retryable": True
                }
            ))
            
            raise HTTPException(status_code=504, detail="Payment timeout")

        except Exception as e:
            logger.error(
                "Payment failed",
                request_id=trace_id,
                order_id=order_id,
                error=str(e)
            )
            
            asyncio.create_task(send_log_to_prodsentinel(
                service_name=SERVICE_NAME,
                trace_id=trace_id,
                level="ERROR",
                message="Payment failed",
                attributes={"order_id": order_id, "error": str(e)}
            ))
            
            raise HTTPException(status_code=500, detail="Payment failure")
