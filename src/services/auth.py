from datetime import UTC, datetime, timedelta, timezone
from typing import Literal, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession
import secrets

from src.db.models.user import User
from src.services.redis import RedisService, get_redis_service
from src.services.user import UserService
from src.db.db import get_db
from src.config.config import settings


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


class Hash:
    """
    Utility class for password hashing and verification.

    Uses bcrypt for secure password handling.
    """

    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def verify_password(self, plain_password, hashed_password):
        """
        Verify a password against a hash.

        Args:
            plain_password: Plain text password to verify
            hashed_password: Hashed password to verify against

        Returns:
            bool: True if password matches, False otherwise
        """
        return self.pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str):
        """
        Generate a password hash.

        Args:
            password: Plain text password to hash

        Returns:
            str: Hashed password
        """
        return self.pwd_context.hash(password)


def create_token(
    data: dict,
    expires_delta: timedelta,
    token_type: Literal["access", "refresh"],
):
    """
    Create a JWT token.

    Args:
        data: Data to encode in the token
        expires_delta: Token expiration time
        token_type: Type of token ("access" or "refresh")

    Returns:
        str: Encoded JWT token
    """
    to_encode = data.copy()
    now = datetime.now(UTC)
    expire = now + expires_delta
    to_encode.update({"exp": expire, "iat": now, "token_type": token_type})
    encoded_jwt = jwt.encode(
        to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM
    )
    return encoded_jwt


async def create_access_token(data: dict, expires_delta: Optional[float] = None) -> str:
    """
    Create a JWT access token.

    Args:
        data: Data to encode in the token
        expires_delta: Optional custom expiration time

    Returns:
        str: Encoded JWT access token
    """
    if expires_delta:
        access_token = create_token(data, expires_delta, "access")
    else:
        access_token = create_token(
            data, timedelta(seconds=settings.JWT_EXPIRATION_SECONDS), "access"
        )
    return access_token


async def create_refresh_token(data: dict, expires_delta: Optional[float] = None):
    """
    Create a JWT refresh token.

    Args:
        data: Data to encode in the token
        expires_delta: Optional custom expiration time

    Returns:
        str: Encoded JWT refresh token
    """
    if expires_delta:
        refresh_token = create_token(data, expires_delta, "refresh")
    else:
        refresh_token = create_token(
            data, timedelta(seconds=settings.JWT_REFRESH_EXPIRATION_SECONDS), "refresh"
        )
    return refresh_token


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
    redis_service: RedisService = Depends(get_redis_service),
):
    """
    Get the current authenticated user from JWT token.

    Args:
        token: JWT token from authorization header
        db: Database session

    Returns:
        User: Current authenticated user

    Raises:
        HTTPException: If token is invalid or user not found
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # Decode JWT
        payload = jwt.decode(
            token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM]
        )
        username = payload["sub"]
        if username is None:
            raise credentials_exception

        # Check if user is in Redis cache
        cache_key = f"user:{username}"
        cached_user = await redis_service.get(cache_key)

        if cached_user:
            # Convert cached dictionary to User model
            user_dict = cached_user
            user = User(
                id=user_dict["id"],
                username=user_dict["username"],
                email=user_dict["email"],
                hashed_password=user_dict["hashed_password"],
                created_at=datetime.fromisoformat(user_dict["created_at"]),
                avatar=user_dict.get("avatar"),
                refresh_token=user_dict.get("refresh_token"),
            )
            return user

        user_service = UserService(db)
        user = await user_service.get_user_by_username(username)
        if user is None:
            raise credentials_exception

        return user

    except JWTError:
        raise credentials_exception


async def create_password_reset_token(data: dict) -> str:
    """
    Create a password reset token.

    Args:
        data: Data to encode in the token (should include user email)

    Returns:
        str: Password reset token
    """
    # Add a unique salt to the token to prevent reuse
    salt = secrets.token_hex(8)
    encoded_data = data.copy()
    encoded_data["salt"] = salt
    encoded_data["token_type"] = "password_reset"
    encoded_data["exp"] = datetime.now(timezone.utc) + timedelta(hours=1)

    return jwt.encode(
        encoded_data, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM
    )


async def verify_password_reset_token(token: str) -> dict | None:
    """
    Verify a password reset token.

    Args:
        token: Password reset token

    Returns:
        dict | None: Token payload if valid, None otherwise
    """
    try:
        payload = jwt.decode(
            token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM]
        )
        if payload.get("token_type") != "password_reset" or "email" not in payload:
            return None
        return payload
    except jwt.JWTError:
        return None
