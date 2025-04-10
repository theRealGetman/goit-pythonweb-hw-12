"""
API routes for contacts management.

This module provides endpoints for CRUD operations on contacts and retrieving contacts
with upcoming birthdays.
"""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.db import get_db
from src.db.models.user import User
from src.schemas.contact import ContactModel, ContactResponse
from src.services.auth import get_current_user
from src.services.contacts import ContactService


router = APIRouter(prefix="/contacts", tags=["contacts"])


@router.get("/", response_model=List[ContactResponse])
async def read_contacts(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    q: str = Query(None, min_length=1, max_length=50),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Retrieve a list of contacts for the authenticated user.

    Supports pagination and filtering by search query.

    Args:
        skip: Number of contacts to skip (pagination offset)
        limit: Maximum number of contacts to return
        q: Optional search query to filter contacts by name or email
        db: Database session
        current_user: Currently authenticated user

    Returns:
        List[ContactResponse]: List of contacts belonging to the user
    """
    contact_service = ContactService(db)
    contacts = await contact_service.get_contacts(current_user, skip, limit, q)
    return contacts


@router.get("/{contact_id}", response_model=ContactResponse)
async def read_contact(
    contact_id: int = Path(gt=0),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Retrieve a specific contact by ID.

    Args:
        contact_id: ID of the contact to retrieve
        db: Database session
        current_user: Currently authenticated user

    Returns:
        ContactResponse: Contact details if found

    Raises:
        HTTPException: If contact is not found
    """
    contact_service = ContactService(db)
    contact = await contact_service.get_contact(contact_id, current_user)
    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contact not found",
        )
    return contact


@router.post("/", response_model=ContactResponse, status_code=status.HTTP_201_CREATED)
async def create_contact(
    body: ContactModel,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Create a new contact for the authenticated user.

    Args:
        body: Contact data to create
        db: Database session
        current_user: Currently authenticated user

    Returns:
        ContactResponse: Newly created contact
    """
    contact_service = ContactService(db)
    return await contact_service.create_contact(body, current_user)


@router.put("/{contact_id}", response_model=ContactResponse)
async def update_contact(
    body: ContactModel,
    contact_id: int = Path(gt=0),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Update an existing contact.

    Args:
        body: Updated contact data
        contact_id: ID of the contact to update
        db: Database session
        current_user: Currently authenticated user

    Returns:
        ContactResponse: Updated contact details

    Raises:
        HTTPException: If contact is not found
    """
    contact_service = ContactService(db)
    contact = await contact_service.update_contact(contact_id, body, current_user)
    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contact not found",
        )
    return contact


@router.delete(
    "/{contact_id}", response_model=ContactResponse, status_code=status.HTTP_200_OK
)
async def delete_contact(
    contact_id: int = Path(gt=0),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Delete a contact.

    Args:
        contact_id: ID of the contact to delete
        db: Database session
        current_user: Currently authenticated user

    Returns:
        ContactResponse: Deleted contact details

    Raises:
        HTTPException: If contact is not found
    """
    contact_service = ContactService(db)
    contact = await contact_service.delete_contact(contact_id, current_user)
    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contact not found",
        )
    return contact


@router.get("/birthdays/", response_model=List[ContactResponse])
async def upcoming_birthdays(
    days: int = Query(7, ge=1, le=365),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Retrieve contacts with birthdays in the next specified number of days.

    Args:
        days: Number of days to check for upcoming birthdays
        db: Database session
        current_user: Currently authenticated user

    Returns:
        List[ContactResponse]: List of contacts with upcoming birthdays
    """
    contact_service = ContactService(db)
    contacts = await contact_service.get_birthdays(days, current_user)
    return contacts
