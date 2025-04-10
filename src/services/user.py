from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession
from libgravatar import Gravatar

from src.db.models.user import User
from src.repository.user import UserRepository
from src.schemas.user import UserCreate

from src.config.config import settings


class UserService:
    """
    Service for user-related operations.

    Handles business logic for user authentication, registration, and profile management.

    Attributes:
        repository: Repository for user database operations
        user: Currently authenticated user
    """

    def __init__(self, db: AsyncSession):
        """
        Initialize UserService with database session.

        Args:
            db: Async database session for database operations
        """
        self.repository = UserRepository(db)
        self.user = None

    async def login(self, username, password):
        """
        Authenticate a user by username and password.

        Args:
            username: User's username
            password: User's password

        Returns:
            bool: True if authentication successful, False otherwise
        """
        # Simulate a login process
        if username == "admin" and password == "password":
            self.user = {"username": username}
            return True
        return False

    async def logout(self):
        """
        Log out the current user by clearing user data.
        """
        self.user = None

    def is_authenticated(self):
        """
        Check if a user is currently authenticated.

        Returns:
            bool: True if a user is authenticated, False otherwise
        """
        return self.user is not None

    async def create_user(self, body: UserCreate) -> User:
        """
        Create a new user with Gravatar avatar.

        Args:
            body: User creation data

        Returns:
            User: Newly created user
        """
        avatar = None
        try:
            gravatar = Gravatar(body.email)
            avatar = gravatar.get_image()
        except Exception as e:
            print(f"Error generating Gravatar: {e}")

        user = await self.repository.create_user(body, avatar)
        return user

    async def get_user_by_id(self, user_id: int) -> User | None:
        """
        Get a user by their ID.

        Args:
            user_id: ID of the user to retrieve

        Returns:
            User: The user if found, None otherwise
        """
        user = await self.repository.get_user_by_id(user_id)
        return user

    async def get_user_by_username(self, username: str) -> User | None:
        """
        Get a user by their username.

        Args:
            username: Username of the user to retrieve

        Returns:
            User: The user if found, None otherwise
        """
        user = await self.repository.get_user_by_username(username=username)
        return user

    async def get_user_by_email(self, email: str) -> User | None:
        """
        Get a user by their email address.

        Args:
            email: Email of the user to retrieve

        Returns:
            User: The user if found, None otherwise
        """
        user = await self.repository.get_user_by_email(email=email)
        return user

    async def verify_refresh_token(self, refresh_token: str) -> User | None:
        """
        Verify a refresh token and get the associated user.

        Args:
            refresh_token: JWT refresh token to verify

        Returns:
            User: The user if token is valid, None otherwise
        """
        try:
            payload = jwt.decode(
                refresh_token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM]
            )
            username: str = payload.get("sub")
            token_type: str = payload.get("token_type")
            if username is None or token_type != "refresh":
                return None
            user = await self.repository.get_user_by_username_and_token(
                username=username, token=refresh_token
            )
            return user
        except JWTError:
            return None

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
        upd_user = await self.repository.save_refresh_token(
            body=body, refresh_token=refresh_token
        )
        if upd_user:
            return upd_user
        return None

    async def update_avatar_url(self, email: str, avatar_url: str) -> User | None:
        """
        Update a user's avatar URL.

        Args:
            email: Email of the user to update
            avatar_url: New avatar URL

        Returns:
            User: Updated user if successful, None otherwise
        """
        return await self.repository.update_avatar_url(email, avatar_url)
