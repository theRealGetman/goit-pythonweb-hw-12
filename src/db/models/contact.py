from sqlalchemy import ForeignKey, Integer, String, Date
from sqlalchemy.orm import Mapped, mapped_column, relationship

from datetime import date as d

from src.db.models.user import User
from src.db.models.base import Base


class Contact(Base):
    """
    Contact model for storing contact information.

    Represents a person's contact details associated with a specific user.

    Attributes:
        id: Unique identifier for the contact
        first_name: Contact's first name
        last_name: Contact's last name
        phone: Contact's phone number
        email: Contact's email address
        date_of_birth: Contact's birthday
        user_id: Foreign key referencing the user who owns this contact
        user: Relationship to the User model
    """

    __tablename__ = "contacts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    first_name: Mapped[str] = mapped_column(String(50))
    last_name: Mapped[str] = mapped_column(String(50))
    phone: Mapped[str] = mapped_column(String(15))
    email: Mapped[str] = mapped_column(String(50))
    date_of_birth: Mapped[d] = mapped_column(Date)

    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=False
    )
    user: Mapped[User] = relationship("User", backref="contacts")
