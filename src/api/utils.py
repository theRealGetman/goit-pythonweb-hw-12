"""
API routes for utility functions and application status.

This module provides endpoints for checking application health and status.
"""

from fastapi import APIRouter, Depends, Request
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.db import get_db


router = APIRouter(prefix="/utils", tags=["utils"])


@router.get("/healthcheck")
async def healthcheck(db: AsyncSession = Depends(get_db)):
    """
    Check the health of the application.

    Performs a database connection test and returns status information.

    Args:
        db: Database session

    Returns:
        dict: Application health status with database connection check
    """
    try:
        # Test database connection
        result = await db.execute(text("SELECT 1"))
        db_status = result.scalar() == 1
    except Exception:
        db_status = False

    return {
        "status": "healthy" if db_status else "unhealthy",
        "database_connected": db_status,
    }


@router.get("/request-info")
async def request_info(request: Request):
    """
    Get detailed information about the current request.

    Used for debugging and diagnostics.

    Args:
        request: Current HTTP request

    Returns:
        dict: Information about the request including headers and client details
    """
    client_host = request.client.host if request.client else "unknown"
    user_agent = request.headers.get("user-agent", "unknown")

    return {
        "client_host": client_host,
        "method": request.method,
        "url": str(request.url),
        "user_agent": user_agent,
        "headers": dict(request.headers),
    }


@router.get("/version")
async def version():
    """
    Get the current API version.

    Returns:
        dict: API version information
    """
    return {"version": "1.0.0", "name": "Contact Management API", "build": "12"}
