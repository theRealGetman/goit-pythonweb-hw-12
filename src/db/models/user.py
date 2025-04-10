from datetime import date
from typing import Optional
from sqlalchemy import DateTime, Integer, String, func
from sqlalchemy.orm import mapped_column, Mapped

from src.db.models.base import Base


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(150), nullable=False, unique=True)
    email: Mapped[str] = mapped_column(String(150), nullable=False, unique=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[date] = mapped_column(DateTime, default=func.now())
    avatar: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    refresh_token: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
