from pydantic import BaseModel, Field, EmailStr


class TokenModel(BaseModel):
    """
    Schema representing authentication tokens.

    Defines the shape of token responses from authentication endpoints.

    Attributes:
        access_token: JWT access token used for authentication
        refresh_token: JWT refresh token used to get new access tokens
        token_type: Type of token, typically "bearer"
    """

    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenRefreshRequest(BaseModel):
    """
    Schema for token refresh requests.

    Used when requesting a new access token using a refresh token.

    Attributes:
        refresh_token: JWT refresh token
    """

    refresh_token: str = Field(..., description="JWT refresh token")


class PasswordResetRequest(BaseModel):
    """
    Password reset request model.

    Contains email for which to reset password.

    Attributes:
        email: Email address of the user requesting password reset
    """

    email: EmailStr


class PasswordResetConfirm(BaseModel):
    """
    Password reset confirmation model.

    Contains token and new password.

    Attributes:
        token: Token received for password reset
        password: New password to set
    """

    token: str
    password: str = Field(min_length=6, max_length=10)
