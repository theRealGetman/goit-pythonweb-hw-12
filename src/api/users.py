"""
API routes for user profile management.

This module provides endpoints for viewing and updating user profiles, including avatar uploads.
"""

from fastapi import (
    APIRouter,
    Depends,
    File,
    HTTPException,
    Path,
    UploadFile,
    status,
)
from sqlalchemy.ext.asyncio import AsyncSession

from src.services.redis import RedisService, get_redis_service
from src.db.db import get_db
from src.db.models.user import User
from src.schemas.user import RoleUpdate, UserResponse
from src.services.auth import get_current_admin, get_current_user
from src.services.upload_file import CloudinaryService
from src.services.user import UserService


router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserResponse)
async def read_user_me(current_user: User = Depends(get_current_user)):
    """
    Retrieve the authenticated user's profile.

    Args:
        current_user: Currently authenticated user

    Returns:
        UserResponse: Current user's profile data
    """
    return current_user


@router.get("/{user_id}", response_model=UserResponse)
async def read_user(
    user_id: int = Path(gt=0),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Retrieve a user's profile by ID.

    Args:
        user_id: ID of the user to retrieve
        db: Database session
        current_user: Currently authenticated user

    Returns:
        UserResponse: User profile data

    Raises:
        HTTPException: If user is not found
    """
    user_service = UserService(db)
    user = await user_service.get_user_by_id(user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return user


@router.patch("/avatar", response_model=UserResponse)
async def update_avatar(
    file: UploadFile = File(),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    redis_service: RedisService = Depends(get_redis_service),
):
    """
    Update the authenticated user's avatar.

    Only admin users can change their avatar. Regular users must use the default avatar.

    Args:
        file: Image file to upload as avatar
        current_user: Currently authenticated user
        db: Database session

    Returns:
        UserResponse: Updated user profile with new avatar URL

    Raises:
        HTTPException: If file upload fails or is invalid
    """
    # Check if user is admin
    if not current_user.is_admin():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can change their avatar",
        )

    cloudinary = CloudinaryService()
    user_service = UserService(db)

    # Validate file type
    if file.content_type not in ["image/jpeg", "image/png", "image/gif"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file type. Only JPEG, PNG, and GIF are allowed.",
        )

    # Upload to Cloudinary
    try:
        contents = await file.read()
        public_id = f"avatar_{current_user.id}"
        upload_result = await cloudinary.upload_image(contents, public_id=public_id)

        # Update user avatar in database
        updated_user = await user_service.update_avatar_url(
            current_user.email, upload_result["secure_url"]
        )

        # Invalidate cache for this user
        cache_key = f"user:{current_user.username}"
        await redis_service.delete(cache_key)

        return updated_user
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload avatar: {str(e)}",
        )


@router.put("/{user_id}/role", response_model=UserResponse)
async def update_user_role(
    user_id: int,
    role_data: RoleUpdate,
    current_user: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
    redis_service: RedisService = Depends(get_redis_service),
):
    """
    Update a user's role (admin only).

    Args:
        user_id: ID of user to update
        role_data: New role data
        current_user: Currently authenticated admin user
        db: Database session
        redis_service: Redis caching service

    Returns:
        UserResponse: Updated user with new role

    Raises:
        HTTPException: If user is not found
    """
    user_service = UserService(db)

    # Check if user exists
    user_to_update = await user_service.get_user_by_id(user_id)
    if not user_to_update:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} not found",
        )

    # Update the user's role
    updated_user = await user_service.change_user_role(user_id, role_data.role)

    # Invalidate cache for the updated user
    cache_key = f"user:{updated_user.username}"
    await redis_service.delete(cache_key)

    return updated_user


@router.get("/", response_model=list[UserResponse])
async def get_all_users(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    """
    Get all users (admin only).

    Args:
        skip: Number of users to skip
        limit: Maximum number of users to return
        current_user: Currently authenticated admin user
        db: Database session

    Returns:
        list[UserResponse]: List of users
    """
    user_service = UserService(db)
    users = await user_service.get_users(skip=skip, limit=limit)
    return users
