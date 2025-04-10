from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession
from libgravatar import Gravatar

from src.db.models.user import User
from src.repository.user import UserRepository
from src.schemas.user import UserCreate

from src.config.config import settings


class UserService:
    def __init__(self, db: AsyncSession):
        self.repository = UserRepository(db)
        self.user = None

    async def login(self, username, password):
        # Simulate a login process
        if username == "admin" and password == "password":
            self.user = {"username": username}
            return True
        return False

    async def logout(self):
        self.user = None

    def is_authenticated(self):
        return self.user is not None

    async def create_user(self, body: UserCreate) -> User:
        avatar = None
        try:
            gravatar = Gravatar(body.email)
            avatar = gravatar.get_image()
        except Exception as e:
            print(f"Error generating Gravatar: {e}")

        user = await self.repository.create_user(body, avatar)
        return user

    async def get_user_by_id(self, user_id: int) -> User | None:
        user = await self.repository.get_user_by_id(user_id)
        return user

    async def get_user_by_username(self, username: str) -> User | None:
        user = await self.repository.get_user_by_username(username=username)
        return user

    async def get_user_by_email(self, email: str) -> User | None:
        user = await self.repository.get_user_by_email(email=email)
        return user

    async def verify_refresh_token(self, refresh_token: str) -> User | None:
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
        upd_user = await self.repository.save_refresh_token(
            body=body, refresh_token=refresh_token
        )
        if upd_user:
            return upd_user
        return None

    async def update_avatar_url(self, email: str, avatar_url: str) -> User | None:
        return await self.repository.update_avatar_url(email, avatar_url)
