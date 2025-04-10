from fastapi import APIRouter, Depends, File, Request, UploadFile
from slowapi import Limiter
from slowapi.util import get_remote_address
from src.services.user import UserService
from src.config.config import settings
from src.services.upload_file import UploadFileService
from src.schemas.user import UserModel
from src.services.auth import get_current_user
from src.db.models.user import User
from src.db.db import get_db
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/users", tags=["users"])
limiter = Limiter(key_func=get_remote_address)


@limiter.limit("10/minute")
@router.get(
    "/me", response_model=UserModel, description="No more than 10 requests per minute"
)
async def me(request: Request, user: User = Depends(get_current_user)):
    return user


@router.patch("/avatar", response_model=UserModel)
async def update_avatar_user(
    file: UploadFile = File(),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    avatar_url = UploadFileService(
        settings.CLD_NAME,
        settings.CLD_API_KEY,
        settings.CLD_API_SECRET,
    ).upload_file(file, user.username)

    user_service = UserService(db)
    user = await user_service.update_avatar_url(user.email, avatar_url)

    return user
