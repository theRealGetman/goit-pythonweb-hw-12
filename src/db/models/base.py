"""
Base SQLAlchemy model definition.

This module defines the base declarative model class from which all other
database models in the application will inherit.
"""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """
    Base class for all SQLAlchemy models.

    All database model classes in the application should inherit from this class
    to ensure consistent behavior and to support SQLAlchemy's declarative mapping system.

    The Base class provides:
    - Table creation capabilities
    - Relationship definitions
    - Session integration
    - ORM mapping functionality
    """

    pass
