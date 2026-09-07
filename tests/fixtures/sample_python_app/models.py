from pydantic import BaseModel
from typing import Optional

class UserLoginRequest(BaseModel):
    """User authentication payload."""
    username: str
    password: str
    remember_me: Optional[bool] = False

class AuthToken(BaseModel):
    """Access token response model."""
    access_token: str
    token_type: str = "bearer"
