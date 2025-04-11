from unittest.mock import AsyncMock, patch
import io

import pytest


def test_get_current_user(client, get_token):
    response = client.get(
        "/api/users/me", headers={"Authorization": f"Bearer {get_token}"}
    )

    assert response.status_code == 200, response.text
    data = response.json()
    assert "username" in data
    assert data["username"] == "deadpool"


def test_get_user_by_id(client, get_token):
    # First get current user to get the ID
    response = client.get(
        "/api/users/me", headers={"Authorization": f"Bearer {get_token}"}
    )
    user = response.json()
    user_id = user["id"]

    # Then get the user by ID
    response = client.get(
        f"/api/users/{user_id}", headers={"Authorization": f"Bearer {get_token}"}
    )

    assert response.status_code == 200, response.text
    data = response.json()
    assert data["id"] == user_id
    assert data["username"] == "deadpool"


def test_get_user_not_found(client, get_token):
    response = client.get(
        "/api/users/9999",  # Assuming this ID doesn't exist
        headers={"Authorization": f"Bearer {get_token}"},
    )

    assert response.status_code == 404, response.text
    data = response.json()
    assert "detail" in data
    assert "not found" in data["detail"]


def test_update_avatar_invalid_file_type(client, admin_token):
    # Create a mock file with invalid type
    file_content = b"fake text content"
    file = io.BytesIO(file_content)

    # Make the request
    response = client.patch(
        "/api/users/avatar",
        headers={"Authorization": f"Bearer {admin_token}"},
        files={"file": ("avatar.txt", file, "text/plain")},
    )

    assert response.status_code == 400, response.text
    data = response.json()
    assert "detail" in data
    assert "Invalid file type" in data["detail"]


# Add these tests
def test_update_avatar_as_regular_user(client, get_token):
    """Test that regular users cannot update their avatar."""
    # Create a mock image file
    file_content = b"fake image content"
    file = io.BytesIO(file_content)

    # Make the request
    response = client.patch(
        "/api/users/avatar",
        headers={"Authorization": f"Bearer {get_token}"},
        files={"file": ("avatar.jpg", file, "image/jpeg")},
    )

    # Should be forbidden for regular users
    assert response.status_code == 403, response.text
    data = response.json()
    assert "detail" in data
    assert "administrators" in data["detail"]


@pytest.mark.asyncio
async def test_update_avatar_as_admin(client, admin_token):
    """Test that admin users can update their avatar."""
    # Mock the CloudinaryService
    with patch("src.api.users.CloudinaryService") as mock_cloudinary_service:
        mock_instance = AsyncMock()
        mock_instance.upload_image.return_value = {
            "secure_url": "https://example.com/avatar.jpg"
        }
        mock_cloudinary_service.return_value = mock_instance

        # Create a mock image file
        file_content = b"fake image content"
        file = io.BytesIO(file_content)

        # Make the request as admin
        response = client.patch(
            "/api/users/avatar",
            headers={"Authorization": f"Bearer {admin_token}"},
            files={"file": ("avatar.jpg", file, "image/jpeg")},
        )

        # Should be allowed for admin users
        assert response.status_code == 200, response.text
        data = response.json()
        assert "avatar" in data
        assert data["avatar"] == "https://example.com/avatar.jpg"

        # Verify the service was called
        mock_instance.upload_image.assert_called_once()


def test_update_user_role(client, get_token, admin_token):
    """Test updating user role (admin only)."""
    # Get ID of regular user
    user_response = client.get(
        "/api/users/me",
        headers={"Authorization": f"Bearer {get_token}"},
    )
    user_id = user_response.json()["id"]

    # Try to update role as regular user (should fail)
    response = client.put(
        f"/api/users/{user_id}/role",
        headers={"Authorization": f"Bearer {get_token}"},
        json={"role": "admin"},
    )
    assert response.status_code == 403, response.text

    # Update role as admin
    response = client.put(
        f"/api/users/{user_id}/role",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"role": "admin"},
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["role"] == "admin"
