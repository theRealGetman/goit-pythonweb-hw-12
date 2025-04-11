from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    HTTPException,
    status,
)
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from src.schemas.user import UserCreate
from src.services.auth import (
    Hash,
    create_access_token,
    create_password_reset_token,
    create_refresh_token,
    verify_password_reset_token,
)
from src.schemas.token import (
    PasswordResetConfirm,
    PasswordResetRequest,
    TokenModel,
    TokenRefreshRequest,
)
from src.services.user import UserService
from src.db.db import get_db


router = APIRouter(prefix="/auth", tags=["auth"])
hash_handler = Hash()


@router.post(
    "/register", response_model=TokenModel, status_code=status.HTTP_201_CREATED
)
async def signup(body: UserCreate, db: AsyncSession = Depends(get_db)):
    """
    Register a new user.

    Creates a new user account and returns authentication tokens.

    Args:
        body: User registration data
        db: Database session

    Returns:
        TokenModel: Access and refresh tokens

    Raises:
        HTTPException: If username or email already exists
    """
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
    """
    Authenticate a user and issue tokens.

    Validates credentials and returns access and refresh tokens.

    Args:
        body: Login credentials
        db: Database session

    Returns:
        TokenModel: Access and refresh tokens

    Raises:
        HTTPException: If credentials are invalid
    """
    user_service = UserService(db)

    user = await user_service.get_user_by_username(body.username)

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
    """
    Get a new access token using a refresh token.

    Validates refresh token and issues a new access token.

    Args:
        request: Refresh token request
        db: Database session

    Returns:
        TokenModel: New access token and existing refresh token

    Raises:
        HTTPException: If refresh token is invalid or expired
    """
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


@router.post("/reset-password/request", status_code=status.HTTP_202_ACCEPTED)
async def request_password_reset(
    body: PasswordResetRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    """
    Request a password reset.

    Sends a password reset token to the user's email address.

    Args:
        body: Password reset request with email
        background_tasks: Background task manager for sending email
        db: Database session

    Returns:
        JSON response indicating the reset email was sent

    Note:
        For security reasons, this endpoint will return success even if
        the email doesn't exist in the database.
    """
    user_service = UserService(db)
    user = await user_service.get_user_by_email(body.email)

    if user:
        # Generate token
        token = await create_password_reset_token({"email": user.email})

        # In a real app, you would send an email here
        # For demonstration, we'll just log it
        print(f"Password reset token for {user.email}: {token}")

        # Example email sending code
        # background_tasks.add_task(
        #     send_password_reset_email, user.email, token
        # )

    # Always return a success response, even if user doesn't exist
    # This prevents email enumeration attacks
    return {
        "message": "If your email exists in our system, you will receive a password reset link"
    }


@router.post("/reset-password/confirm", status_code=status.HTTP_200_OK)
async def confirm_password_reset(
    body: PasswordResetConfirm, db: AsyncSession = Depends(get_db)
):
    """
    Complete the password reset process.

    Verifies the token and updates the user's password.

    Args:
        body: Reset confirmation with token and new password
        db: Database session

    Returns:
        JSON response indicating the password was reset

    Raises:
        HTTPException: If token is invalid or expired
    """
    # Verify token
    payload = await verify_password_reset_token(body.token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired refresh token",
        )

    email = payload.get("email")

    # Update password
    user_service = UserService(db)
    hashed_password = hash_handler.get_password_hash(body.password)
    user = await user_service.update_password(email, hashed_password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    return {"message": "Password has been reset successfully"}
