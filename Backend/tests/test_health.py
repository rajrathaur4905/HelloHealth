"""
Health Check Endpoint Tests.

Verifies the GET /api/v1/health endpoint returns correct status
information about the application and its components.

Tests:
  1. Health endpoint returns 200 OK
  2. Response status is "healthy" or "degraded" (never missing)
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_returns_200(client: AsyncClient):
    """GET /api/v1/health should return 200 even if some components are down."""
    response = await client.get("/api/v1/health")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_health_status_value(client: AsyncClient):
    """Health response status must be either 'healthy' or 'degraded'.

    The health endpoint reports overall system status:
      - 'healthy' = all components operational
      - 'degraded' = one or more components unavailable but app is running

    In the test environment (SQLite), the database check may show as
    degraded since we're not using PostgreSQL — both values are valid.
    """
    response = await client.get("/api/v1/health")
    data = response.json()

    assert "status" in data, "Response must include 'status' field"
    assert data["status"] in ("healthy", "degraded"), (
        f"Expected 'healthy' or 'degraded', got '{data['status']}'"
    )
    assert "components" in data, "Response must include 'components' field"
    assert "app" in data, "Response must include 'app' field"
