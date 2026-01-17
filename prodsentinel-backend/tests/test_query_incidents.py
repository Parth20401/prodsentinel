import pytest
from httpx import AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_list_incidents_empty(async_client: AsyncClient):
    """
    Test that the /query/incidents endpoint returns a valid paginated response (even if empty).
    """
    response = await async_client.get("/query/incidents")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert "limit" in data
    assert "offset" in data
    assert isinstance(data["items"], list)

@pytest.mark.asyncio
async def test_get_analysis_404(async_client: AsyncClient):
    """
    Test that getting analysis for a non-existent incident returns 404 (or null if we handled it that way, but router raises 404).
    """
    # Use a random UUID
    import uuid
    random_id = str(uuid.uuid4())
    response = await async_client.get(f"/query/incidents/{random_id}/analysis")
    assert response.status_code == 404
