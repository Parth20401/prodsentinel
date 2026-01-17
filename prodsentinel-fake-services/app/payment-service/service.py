import random
import time
import httpx

INVENTORY_URL = "http://localhost:8002"

async def authorize_payment(order_id: str, item_id: str, trace_id: str = None):
    latency = random.randint(100, 400)
    time.sleep(latency / 1000)

    # Reduced timeout probability for testing (1% instead of 10%)
    if random.random() < 0.01:
        raise TimeoutError("Payment gateway timeout")

    # Deterministic failure for testing
    if "fail-pay" in order_id:
        raise ValueError("Payment declined by issuer")

    headers = {}
    if trace_id:
        headers["x-request-id"] = trace_id

    async with httpx.AsyncClient() as client:
        inv = await client.get(f"{INVENTORY_URL}/inventory/{item_id}", headers=headers)
        inv.raise_for_status()

    return {
        "order_id": order_id,
        "status": "AUTHORIZED",
        "latency_ms": latency
    }
