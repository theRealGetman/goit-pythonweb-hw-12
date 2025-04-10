from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from src.schemas.user import UserCreate
from src.services.auth import Hash, create_access_token, create_refresh_token
from src.schemas.token import TokenModel, TokenRefreshRequest
from src.services.user import UserService
from src.db.db import get_db


router = APIRouter(prefix="/auth", tags=["auth"])
hash_handler = Hash()


@router.post(
    "/register", response_model=TokenModel, status_code=status.HTTP_201_CREATED
)
async def signup(body: UserCreate, db: AsyncSession = Depends(get_db)):
    user_service = UserService(db)

    exist_user = await user_service.get_user_by_email(body.email)
    if exist_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Account already exists",
        )

    exist_user = await user_service.get_user_by_username(body.username)
    if exist_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Account already exists",
        )

    password = body.password
    body.password = hash_handler.get_password_hash(body.password)
    await user_service.create_user(body)

    return await login(
        body=OAuth2PasswordRequestForm(username=body.username, password=password),
        db=db,
    )


@router.post("/login", response_model=TokenModel)
async def login(
    body: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)
):
    user_service = UserService(db)

    user = await user_service.get_user_by_username(body.username)

    print(body.password, user.hashed_password)
    if not user or not hash_handler.verify_password(
        body.password, user.hashed_password
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )

    # Generate JWT
    access_token = await create_access_token(data={"sub": user.username})
    refresh_token = await create_refresh_token(data={"sub": user.username})
    await user_service.save_refresh_token(body=user, refresh_token=refresh_token)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@router.post("/refresh-token", response_model=TokenModel)
async def new_token(request: TokenRefreshRequest, db: AsyncSession = Depends(get_db)):
    user_service = UserService(db)

    user = await user_service.verify_refresh_token(request.refresh_token)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        )
    new_access_token = await create_access_token(data={"sub": user.username})

    return {
        "access_token": new_access_token,
        "refresh_token": request.refresh_token,
        "token_type": "bearer",
    }
