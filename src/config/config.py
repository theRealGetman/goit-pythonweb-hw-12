"""
Application configuration settings.

This module defines application configuration settings loaded from environment variables.
"""

from pydantic import ConfigDict
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.

    Attributes:
        DB_URL: Database connection URL
        JWT_SECRET: Secret key for JWT token signing
        JWT_ALGORITHM: Algorithm used for JWT token signing
        JWT_EXPIRATION_SECONDS: Access token expiration time in seconds
        JWT_REFRESH_EXPIRATION_SECONDS: Refresh token expiration time in seconds
        CLD_NAME: Cloudinary cloud name
        CLD_API_KEY: Cloudinary API key
        CLD_API_SECRET: Cloudinary API secret
        CLD_URL: Cloudinary URL
        REDIS_HOST: Redis host address
        REDIS_PORT: Redis port number
        REDIS_PASSWORD: Redis password (optional)
        REDIS_USER_CACHE_EXPIRE: Time to cache user data in seconds
    """

    DB_URL: str

    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_SECONDS: int = 3600
    JWT_REFRESH_EXPIRATION_SECONDS: int = 3600 * 24 * 7  # 7 days

    CLD_NAME: str
    CLD_API_KEY: str
    CLD_API_SECRET: str
    CLD_URL: str

    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: str = ""
    REDIS_USER_CACHE_EXPIRE: int = 3600  # 1 hour in seconds

    model_config = ConfigDict(
        extra="ignore", env_file=".env", env_file_encoding="utf-8", case_sensitive=True
    )


settings = Settings()
