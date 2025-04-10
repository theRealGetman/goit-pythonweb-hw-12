from typing import List
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Path,
    Query,
    status,
)

from src.services.auth import get_current_user
from src.db.models.user import User
from src.services.contacts import ContactService
from src.schemas.contact import ContactModel, ContactResponse
from src.db.db import get_db
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/contacts", tags=["contacts"])


@router.get("/", response_model=List[ContactResponse])
async def get_contacts(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
    skip: int = 0,
    limit: int = Query(default=10, le=100, ge=10),
    q: str | None = None,
):
    contact_service = ContactService(db)
    contacts = await contact_service.get_contacts(
        user=user, skip=skip, limit=limit, q=q
    )
    return contacts


@router.get("/birthdays", response_model=List[ContactResponse])
async def get_birthdays(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
    days: int = Query(default=7, ge=1, le=30),
):
    contact_service = ContactService(db)
    contacts = await contact_service.get_birthdays(user=user, days=days)
    return contacts


@router.get("/{contact_id}", response_model=ContactResponse)
async def get_contact(
    contact_id: int = Path(description="The ID of the note to get", gt=0),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    contact_service = ContactService(db)
    contact = await contact_service.get_contact(contact_id, user)
    if contact is None:
        raise HTTPException(status_code=404, detail="Contact not found")
    return contact


@router.post("/", response_model=ContactResponse, status_code=status.HTTP_201_CREATED)
async def create_contact(
    body: ContactModel,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    contact_service = ContactService(db)
    return await contact_service.create_contact(body, user)


@router.put("/{contact_id}", response_model=ContactResponse)
async def update_contact(
    body: ContactModel,
    contact_id: int = Path(description="The ID of the contact to update", gt=0),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    contact_service = ContactService(db)
    contact = await contact_service.update_contact(contact_id, body, user)
    if contact is None:
        raise HTTPException(status_code=404, detail="Contact not found")
    return contact


@router.delete("/{contact_id}", response_model=ContactResponse)
async def delete_contact(
    contact_id: int = Path(description="The ID of the contact to delete", gt=0),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    contact_service = ContactService(db)
    contact = await contact_service.delete_contact(contact_id, user)
    if contact is None:
        raise HTTPException(status_code=404, detail="Contact not found")
    return contact
