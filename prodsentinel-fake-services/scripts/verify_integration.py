import asyncio
import httpx
import asyncpg
import json
import sys
import os

# Configuration
GATEWAY_URL = "http://localhost:8000"
BACKEND_HEALTH_URL = "http://localhost:8080/ingest/health"
# SQLAlchemy uses postgresql+asyncpg://, but asyncpg.create_pool needs postgresql://
DB_DSN = os.getenv("DATABASE_URL", "postgresql://prodsentinel:prodsentinel@localhost:5432/prodsentinel")
# Remove +asyncpg if present (SQLAlchemy format)
DB_DSN = DB_DSN.replace("postgresql+asyncpg://", "postgresql://")

async def check_backend_health():
    print(f"Checking backend health at {BACKEND_HEALTH_URL}...")
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(BACKEND_HEALTH_URL)
            if resp.status_code == 200:
                print("✅ Backend is HEALTHY")
                return True
            else:
                print(f"❌ Backend is UNHEALTHY: {resp.status_code} {resp.text}")
                return False
    except Exception as e:
        print(f"❌ Could not connect to backend: {e}")
        return False

async def trigger_checkout():
    order_id = "test-order-verify"
    print(f"\nTriggering checkout for {order_id}...")
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(f"{GATEWAY_URL}/checkout/{order_id}")
            if resp.status_code == 200:
                print("✅ Checkout SUCCESS")
                return order_id
            else:
                print(f"❌ Checkout FAILED: {resp.status_code} {resp.text}")
                print(f"   Check the api-gateway logs for details")
                return None
    except httpx.ConnectError as e:
        print(f"❌ Could not connect to gateway at {GATEWAY_URL}")
        print(f"   Make sure the api-gateway is running on port 8000")
        print(f"   Error: {e}")
        return None
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return None

async def verify_db_ingestion(order_id):
    print(f"\nVerifying ingestion in database for order {order_id}...")
    try:
        pool = await asyncpg.create_pool(DB_DSN)
        async with pool.acquire() as conn:
            # Check for logs containing the order_id in attributes or message
            rows = await conn.fetch("""
                SELECT service_name, payload 
                FROM raw_signals 
                WHERE signal_type = 'log' 
                AND (payload::text LIKE $1)
                ORDER BY timestamp DESC
            """, f"%{order_id}%")
            
            if rows:
                print(f"✅ Found {len(rows)} log entries for this order!")
                for row in rows:
                    payload = json.loads(row['payload'])
                    print(f"   - [{row['service_name']}] {payload.get('message')}")
                return True
            else:
                print("❌ No logs found in database for this order!")
                return False
    except Exception as e:
        print(f"❌ Database verification failed: {e}")
        return False

async def main():
    if not await check_backend_health():
        sys.exit(1)
        
    order_id = await trigger_checkout()
    if not order_id:
        sys.exit(1)
        
    # Give it a moment for async ingestion
    print("Waiting 2 seconds for ingestion...")
    await asyncio.sleep(2)
    
    if await verify_db_ingestion(order_id):
        print("\n🎉 SUCCESS: End-to-end integration verified!")
    else:
        print("\n❌ FAILURE: Telemetry not ingested.")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
