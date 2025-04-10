from typing import List
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models.user import User
from src.db.models.contact import Contact
from src.repository.contacts import ContactRepository
from src.schemas.contact import ContactModel


class ContactService:
    """
    Service for contact-related operations.

    Handles business logic for contacts and coordinates with the repository layer.
    """

    def __init__(self, db: AsyncSession):
        """
        Initialize ContactService with a database session.

        Args:
            db: Async database session
        """
        self.repository = ContactRepository(db)

    async def get_contacts(
        self, user: User, skip: int = 0, limit: int = 100, q: str | None = None
    ) -> List[Contact]:
        """
        Retrieve a paginated list of contacts for a user with optional search.

        Args:
            user: User whose contacts to retrieve
            skip: Number of contacts to skip (pagination offset)
            limit: Maximum number of contacts to return
            q: Optional search query to filter contacts

        Returns:
            List[Contact]: List of matching contacts
        """
        return await self.repository.get_contacts(user, skip, limit, q)

    async def get_contact(self, contact_id: int, user: User) -> Contact | None:
        """
        Retrieve a specific contact by ID for a user.

        Args:
            contact_id: ID of contact to retrieve
            user: User who owns the contact

        Returns:
            Contact: Contact if found, None otherwise
        """
        return await self.repository.get_contact(contact_id, user)

    async def create_contact(self, body: ContactModel, user: User) -> Contact:
        """
        Create a new contact for a user.

        Args:
            body: Contact data
            user: User who will own the contact

        Returns:
            Contact: Newly created contact
        """
        return await self.repository.create_contact(body, user)

    async def update_contact(
        self, contact_id: int, body: ContactModel, user: User
    ) -> Contact | None:
        """
        Update an existing contact for a user.

        Args:
            contact_id: ID of contact to update
            body: New contact data
            user: User who owns the contact

        Returns:
            Contact: Updated contact if found, None otherwise
        """
        return await self.repository.update_contact(contact_id, body, user)

    async def delete_contact(self, contact_id: int, user: User) -> Contact | None:
        """
        Delete a contact for a user.

        Args:
            contact_id: ID of contact to delete
            user: User who owns the contact

        Returns:
            Contact: Deleted contact if found, None otherwise
        """
        return await self.repository.delete_contact(contact_id, user)

    async def get_birthdays(self, days: int, user: User) -> List[Contact]:
        """
        Get contacts with birthdays in the next specified number of days.

        Args:
            days: Number of days to check for upcoming birthdays
            user: User whose contacts to check

        Returns:
            List[Contact]: List of contacts with upcoming birthdays
        """
        return await self.repository.get_birthdays(days, user)
