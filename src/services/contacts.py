from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models.user import User
from src.repository.contacts import ContactRepository
from src.schemas.contact import ContactModel


class ContactService:
    def __init__(self, db: AsyncSession):
        self.repository = ContactRepository(db)

    async def get_contacts(
        self,
        user: User,
        skip: int = 0,
        limit: int = 100,
        q: str | None = None,
    ):
        return await self.repository.get_contacts(user, skip, limit, q)

    async def get_contact(
        self,
        contact_id: int,
        user: User,
    ):
        return await self.repository.get_contact(contact_id, user)

    async def create_contact(
        self,
        body: ContactModel,
        user: User,
    ):
        return await self.repository.create_contact(body, user)

    async def update_contact(
        self,
        contact_id: int,
        body: ContactModel,
        user: User,
    ):
        return await self.repository.update_contact(contact_id, body, user)

    async def delete_contact(
        self,
        contact_id: int,
        user: User,
    ):
        return await self.repository.delete_contact(contact_id, user)

    async def get_birthdays(
        self,
        days: int,
        user: User,
    ):
        return await self.repository.get_birthdays(days, user)
