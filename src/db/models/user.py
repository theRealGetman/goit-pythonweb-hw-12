from datetime import date
from typing import Optional
from sqlalchemy import DateTime, Enum, Integer, String, func
from sqlalchemy.orm import mapped_column, Mapped

from src.db.models.base import Base


class UserRole(str, Enum):
    """User roles for permission system."""

    USER = "user"
    ADMIN = "admin"


class User(Base):
    """
    User model representing application users.

    Stores user authentication information, profile details, and tokens for authentication.

    Attributes:
        id: Unique identifier for the user
        username: User's unique username
        email: User's unique email address
        hashed_password: Securely stored password hash
        created_at: Timestamp when user account was created
        avatar: URL to user's profile picture
        refresh_token: JWT refresh token for authentication
        role: User role (admin or user)
    """

    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(150), nullable=False, unique=True)
    email: Mapped[str] = mapped_column(String(150), nullable=False, unique=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[date] = mapped_column(DateTime, default=func.now())
    avatar: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    refresh_token: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    role: Mapped[str] = mapped_column(
        String(50),
        default=UserRole.USER,
    )

    def is_admin(self):
        """Check if user has admin role."""
        return self.role == UserRole.ADMIN
