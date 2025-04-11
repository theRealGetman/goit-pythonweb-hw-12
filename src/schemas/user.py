from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, EmailStr, Field, ConfigDict


class UserBase(BaseModel):
    """
    Base schema for user data.

    Contains common fields used across user-related schemas.

    Attributes:
        username: User's unique username
        email: User's unique email address
    """

    username: str = Field(min_length=5, max_length=16)
    email: EmailStr


class UserCreate(UserBase):
    """
    Schema for user registration.

    Extends UserBase to include password field for user creation.

    Attributes:
        password: User's password (stored as hash in database)
    """

    password: str = Field(min_length=6, max_length=10)


class UserResponse(UserBase):
    """
    Schema for user data in responses.

    Used for API responses containing user data.

    Attributes:
        id: User's unique identifier
        username: User's username
        email: User's email address
        avatar: URL to user's avatar image
        created_at: Timestamp when the user was created
    """

    id: int
    username: str
    email: str
    avatar: Optional[str]
    created_at: datetime
    role: str

    model_config = ConfigDict(from_attributes=True)


class UserUpdate(BaseModel):
    """
    Schema for user profile updates.

    Contains fields that can be updated in a user profile.

    Attributes:
        username: New username (optional)
        email: New email address (optional)
        password: New password (optional)
    """

    username: Optional[str] = Field(min_length=5, max_length=16, default=None)
    email: Optional[EmailStr] = None
    password: Optional[str] = Field(min_length=6, max_length=10, default=None)


class RoleUpdate(BaseModel):
    """
    Schema for updating a user's role.

    Attributes:
        role: New role to assign (must be 'user' or 'admin')
    """

    # Use Literal type to restrict values to exact strings
    role: Literal["user", "admin"]
