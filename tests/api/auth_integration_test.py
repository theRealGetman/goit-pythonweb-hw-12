import pytest
from unittest.mock import AsyncMock, Mock, patch

from tests.conftest import test_user

new_user_data = {
    "username": "ironman",
    "email": "tony.stark@example.com",
    "password": "password1",  # Meets 6-10 char requirement
}


def test_register_user(client, monkeypatch):
    # Mock Gravatar service
    with patch("src.services.user.Gravatar") as mock_gravatar:
        mock_gravatar_instance = Mock()
        mock_gravatar_instance.get_image.return_value = "http://example.com/avatar.jpg"
        mock_gravatar.return_value = mock_gravatar_instance

        response = client.post("/api/auth/register", json=new_user_data)

        assert response.status_code == 201, response.text
        data = response.json()
        assert data["access_token"]
        assert data["refresh_token"]
        assert data["token_type"] == "bearer"


def test_register_existing_user(client):
    response = client.post("/api/auth/register", json=test_user)

    assert response.status_code == 409, response.text
    data = response.json()
    assert "detail" in data
    assert "already exists" in data["detail"]


def test_login_valid_credentials(client):
    response = client.post(
        "/api/auth/login",
        data={
            "username": test_user["username"],
            "password": test_user["password"],
        },
    )

    assert response.status_code == 200, response.text
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


def test_login_invalid_password(client):
    response = client.post(
        "/api/auth/login",
        data={
            "username": test_user["username"],
            "password": "wrongpassword",
        },
    )

    assert response.status_code == 401, response.text
    data = response.json()
    assert "detail" in data
    assert "Invalid username or password" in data["detail"]


def test_login_invalid_username(client):
    response = client.post(
        "/api/auth/login",
        data={
            "username": "nonexistentuser",
            "password": test_user["password"],
        },
    )

    assert response.status_code == 401, response.text
    data = response.json()
    assert "detail" in data
    assert "Invalid username or password" in data["detail"]


def test_refresh_token(client, get_token):
    # First login to get a refresh token
    response = client.post(
        "/api/auth/login",
        data={
            "username": test_user["username"],
            "password": test_user["password"],
        },
    )
    refresh_token = response.json()["refresh_token"]

    # Then use the refresh token to get a new access token
    response = client.post(
        "/api/auth/refresh-token",
        json={"refresh_token": refresh_token},
    )

    assert response.status_code == 200, response.text
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


def test_refresh_token_invalid(client):
    response = client.post(
        "/api/auth/refresh-token",
        json={"refresh_token": "invalid_token"},
    )

    assert response.status_code == 401, response.text
    data = response.json()
    assert "detail" in data
    assert "Invalid or expired refresh token" in data["detail"]


def test_request_password_reset(client):
    # Test with existing email
    response = client.post(
        "/api/auth/reset-password/request", json={"email": test_user["email"]}
    )

    # Should always return 202 Accepted
    assert response.status_code == 202, response.text
    data = response.json()
    assert "message" in data
    assert "receive a password reset link" in data["message"]

    # Test with non-existent email
    response = client.post(
        "/api/auth/reset-password/request", json={"email": "nonexistent@example.com"}
    )

    # Should still return 202 Accepted
    assert response.status_code == 202, response.text
    data = response.json()
    assert "message" in data
    assert "receive a password reset link" in data["message"]


def test_confirm_password_reset_invalid_token(client):
    response = client.post(
        "/api/auth/reset-password/confirm",
        json={"token": "invalid_token", "password": "newpass123"},
    )

    assert response.status_code == 400, response.text
    data = response.json()
    assert "detail" in data
    assert "Invalid or expired refresh token" in data["detail"]


@pytest.mark.asyncio
async def test_confirm_password_reset_valid_token(client, monkeypatch):
    # Mock the verify_password_reset_token function
    mock_verify = AsyncMock(return_value={"email": test_user["email"]})
    monkeypatch.setattr("src.api.auth.verify_password_reset_token", mock_verify)

    # Test with valid token
    response = client.post(
        "/api/auth/reset-password/confirm",
        json={"token": "valid_mock_token", "password": "newpass1"},
    )

    assert response.status_code == 200, response.text
    data = response.json()
    assert "message" in data
    assert "successfully" in data["message"]

    # Verify login works with new password
    response = client.post(
        "/api/auth/login",
        data={
            "username": test_user["username"],
            "password": "newpass1",
        },
    )

    assert response.status_code == 200, response.text
    data = response.json()
    assert "access_token" in data
