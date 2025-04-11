import pytest
from unittest.mock import AsyncMock, patch


def test_healthcheck(client):
    response = client.get("/api/utils/healthcheck")

    assert response.status_code == 200, response.text
    data = response.json()
    assert "status" in data
    assert data["status"] == "healthy"
    assert "database_connected" in data
    assert data["database_connected"] == True


def test_request_info(client):
    response = client.get("/api/utils/request-info")

    assert response.status_code == 200, response.text
    data = response.json()
    assert "client_host" in data
    assert "method" in data
    assert data["method"] == "GET"
    assert "url" in data
    assert "user_agent" in data
    assert "headers" in data


def test_version(client):
    response = client.get("/api/utils/version")

    assert response.status_code == 200, response.text
    data = response.json()
    assert "version" in data
    assert "name" in data
    assert "build" in data


def test_healthcheck_db_failure(client):
    # Mock the db.execute to raise an exception
    with patch(
        "sqlalchemy.ext.asyncio.AsyncSession.execute",
        side_effect=Exception("DB connection error"),
    ):
        response = client.get("/api/utils/healthcheck")

        assert response.status_code == 200, response.text
        data = response.json()
        assert "status" in data
        assert data["status"] == "unhealthy"
        assert "database_connected" in data
        assert data["database_connected"] == False
