from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.schemas.user import UserCreate
from src.db.models.user import User


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_user_by_id(self, user_id: int) -> User | None:
        stmt = select(User).filter_by(id=user_id)
        user = await self.session.execute(stmt)
        return user.scalar_one_or_none()

    async def get_user_by_username(self, username: str) -> User | None:
        stmt = select(User).filter_by(username=username)
        user = await self.session.execute(stmt)
        return user.scalar_one_or_none()

    async def get_user_by_email(self, email: str) -> User | None:
        stmt = select(User).filter_by(email=email)
        user = await self.session.execute(stmt)
        return user.scalar_one_or_none()

    async def create_user(self, body: UserCreate, avatar: str = None) -> User:
        user = User(
            **body.model_dump(exclude_unset=True, exclude={"password"}),
            hashed_password=body.password,
            avatar=avatar,
        )
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def get_user_by_username_and_token(self, username, token) -> User | None:
        stmt = select(User).filter_by(username=username, refresh_token=token)
        user = await self.session.execute(stmt)
        return user.scalar_one_or_none()

    async def update_user(self, user_id, user_data) -> User | None:
        # Logic to update a user's information in the database
        pass

    async def delete_user(self, user_id) -> User | None:
        stmt = select(User).filter_by(id=user_id)
        user = await self.session.execute(stmt)
        user = user.scalar_one_or_none()
        if user:
            await self.session.delete(user)
            await self.session.commit()
        return user

    async def save_refresh_token(
        self, body: UserCreate, refresh_token: str
    ) -> User | None:
        stmt = select(User).filter_by(username=body.username)
        user = await self.session.execute(stmt)
        user = user.scalar_one_or_none()
        if user:
            user.refresh_token = refresh_token
            await self.session.commit()
            await self.session.refresh(user)
        return user

    async def update_avatar_url(self, email: str, url: str) -> User:
        user = await self.get_user_by_email(email)
        if user:
            user.avatar = url
            await self.session.commit()
            await self.session.refresh(user)
        return user
