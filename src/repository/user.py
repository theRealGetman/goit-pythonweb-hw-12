from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.schemas.user import UserCreate
from src.db.models.user import User


class UserRepository:
    """
    Repository for user database operations.

    Handles CRUD operations for user data in the database.
    """

    def __init__(self, session: AsyncSession):
        """
        Initialize UserRepository with database session.

        Args:
            session: Async database session for database operations
        """
        self.session = session

    async def get_user_by_id(self, user_id: int) -> User | None:
        """
        Get a user by their ID.

        Args:
            user_id: ID of the user to retrieve

        Returns:
            User: The user if found, None otherwise
        """
        stmt = select(User).filter_by(id=user_id)
        user = await self.session.execute(stmt)
        return user.scalar_one_or_none()

    async def get_user_by_username(self, username: str) -> User | None:
        """
        Get a user by their username.

        Args:
            username: Username of the user to retrieve

        Returns:
            User: The user if found, None otherwise
        """
        stmt = select(User).filter_by(username=username)
        user = await self.session.execute(stmt)
        return user.scalar_one_or_none()

    async def get_user_by_email(self, email: str) -> User | None:
        """
        Get a user by their email address.

        Args:
            email: Email of the user to retrieve

        Returns:
            User: The user if found, None otherwise
        """
        stmt = select(User).filter_by(email=email)
        user = await self.session.execute(stmt)
        return user.scalar_one_or_none()

    async def create_user(self, body: UserCreate, avatar: str = None) -> User:
        """
        Create a new user.

        Args:
            body: User creation data
            avatar: Optional avatar URL

        Returns:
            User: Newly created user
        """
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
        """
        Get a user by username and refresh token.

        Used for validating refresh tokens.

        Args:
            username: Username of the user to retrieve
            token: Refresh token to match

        Returns:
            User: The user if found with matching token, None otherwise
        """
        stmt = select(User).filter_by(username=username, refresh_token=token)
        user = await self.session.execute(stmt)
        return user.scalar_one_or_none()

    async def update_user(self, user_id, user_data) -> User | None:
        """
        Update a user's information.

        Args:
            user_id: ID of the user to update
            user_data: New user data

        Returns:
            User: Updated user if successful, None otherwise
        """
        # Logic to update a user's information in the database
        pass

    async def delete_user(self, user_id) -> User | None:
        """
        Delete a user.

        Args:
            user_id: ID of the user to delete

        Returns:
            User: Deleted user if successful, None otherwise
        """
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
        """
        Save a refresh token for a user.

        Args:
            body: User data
            refresh_token: JWT refresh token to save

        Returns:
            User: Updated user if successful, None otherwise
        """
        stmt = select(User).filter_by(username=body.username)
        user = await self.session.execute(stmt)
        user = user.scalar_one_or_none()
        if user:
            user.refresh_token = refresh_token
            await self.session.commit()
            await self.session.refresh(user)
        return user

    async def update_avatar_url(self, email: str, url: str) -> User:
        """
        Update a user's avatar URL.

        Args:
            email: Email of the user to update
            url: New avatar URL

        Returns:
            User: Updated user if successful, None otherwise
        """
        user = await self.get_user_by_email(email)
        if user:
            user.avatar = url
            await self.session.commit()
            await self.session.refresh(user)
        return user
