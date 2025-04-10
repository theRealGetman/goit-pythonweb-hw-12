from datetime import date
from typing import Optional
from pydantic import BaseModel, ConfigDict, EmailStr


class ContactModel(BaseModel):
    first_name: str
    last_name: str
    phone: str
    email: EmailStr
    date_of_birth: Optional[date] = None


class ContactResponse(ContactModel):
    id: int

    model_config = ConfigDict(from_attributes=True)
