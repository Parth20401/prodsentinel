import random
import time

def check_inventory(item_id: str):
    """
    Simulates inventory lookup with occasional failures.
    """

    latency = random.randint(20, 80)
    time.sleep(latency / 1000)

    if random.random() < 0.05:
        raise RuntimeError("Inventory DB unavailable")

    return {
        "item_id": item_id,
        "available": random.choice([True, True, True, False]),
        "latency_ms": latency
    }
