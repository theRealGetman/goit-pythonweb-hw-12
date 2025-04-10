from datetime import date
from typing import Optional
from pydantic import BaseModel, ConfigDict, EmailStr


class ContactModel(BaseModel):
    """
    Schema for contact creation and updates.

    Validates incoming data for creating or updating contacts.

    Attributes:
        first_name: Contact's first name
        last_name: Contact's last name
        phone: Contact's phone number
        email: Contact's email address (validated as email)
        date_of_birth: Contact's birthday (optional)
    """

    first_name: str
    last_name: str
    phone: str
    email: EmailStr
    date_of_birth: Optional[date] = None


class ContactResponse(ContactModel):
    """
    Schema for contact responses.

    Extends the ContactModel to include the ID for API responses.

    Attributes:
        id: Unique identifier for the contact
    """

    id: int

    model_config = ConfigDict(from_attributes=True)
