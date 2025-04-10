from pydantic import BaseModel, Field


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
